import ast
import json
import math
import re
import time
from datetime import datetime, timezone
from urllib.parse import unquote

from bs4 import BeautifulSoup

from .cache import TTLCache
from .config import (
    BASE_URL,
    LIVE_CACHE_TTL_SECONDS,
    LIVE_COUNTER_MAP,
    RTS_INIT_URL,
    SECONDS_NAME_ALIASES,
)
from .fetcher import fetch_text


class SafeExpressionEvaluator:
    def __init__(self, seconds_values: dict[str, float]) -> None:
        self._seconds_values = seconds_values

    def evaluate(self, expression: str) -> float:
        node = ast.parse(expression, mode="eval")
        return float(self._eval_node(node.body))

    def _eval_node(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError("Unsupported constant value in formula.")

        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            raise ValueError("Unsupported binary operator in formula.")

        if isinstance(node, ast.UnaryOp):
            value = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return value
            if isinstance(node.op, ast.USub):
                return -value
            raise ValueError("Unsupported unary operator in formula.")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Unsupported function call in formula.")

            fn_name = node.func.id
            args = [self._eval_node(arg) for arg in node.args]
            if fn_name == "pow" and len(args) == 2:
                return float(pow(args[0], args[1]))
            if fn_name == "round_js" and len(args) == 1:
                return float(js_round(args[0]))
            raise ValueError(f"Unsupported function {fn_name} in formula.")

        if isinstance(node, ast.Subscript):
            if not isinstance(node.value, ast.Name) or node.value.id != "seconds_values":
                raise ValueError("Unsupported subscript target in formula.")

            key = self._extract_key(node.slice)
            if key not in self._seconds_values:
                raise ValueError(f"Missing seconds variable {key}.")
            return float(self._seconds_values[key])

        raise ValueError("Unsupported expression node in formula.")

    def _extract_key(self, node: ast.AST) -> str:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value

        if hasattr(ast, "Index") and isinstance(node, ast.Index):
            value = node.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                return value.value

        raise ValueError("Invalid seconds key in formula.")


class LiveCountersService:
    def __init__(self, cache: TTLCache) -> None:
        self._cache = cache

    async def get_live_counters(self) -> dict[str, object]:
        cached = self._cache.get("live-counters", LIVE_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        homepage_html = await fetch_text(f"{BASE_URL}/")
        rel_keys = self._collect_rel_keys(homepage_html)

        init_data = await self._fetch_init_data()
        counters = init_data.get("counters")
        if not isinstance(counters, dict):
            raise ValueError("Invalid live counter payload.")

        needed_seconds = collect_formula_seconds_variables(counters, rel_keys)
        seconds_values = build_seconds_context(init_data, needed_seconds)

        values_by_rel: dict[str, int | None] = {}
        for rel_key in rel_keys:
            base_key, action = split_rel_key(rel_key)
            counter = counters.get(base_key)
            if not isinstance(counter, dict):
                values_by_rel[rel_key] = None
                continue

            formula = select_counter_formula(counter, action)
            if formula is None:
                values_by_rel[rel_key] = None
                continue

            try:
                values_by_rel[rel_key] = evaluate_formula(formula, seconds_values)
            except ValueError:
                values_by_rel[rel_key] = None

        grouped: dict[str, dict[str, int | None]] = {}
        for section_name, fields in LIVE_COUNTER_MAP.items():
            grouped[section_name] = {}
            for response_field, rel_key in fields.items():
                grouped[section_name][response_field] = values_by_rel.get(rel_key)

        payload: dict[str, object] = {
            "updated_at": datetime.now(tz=timezone.utc).isoformat(),
            "source": "worldometers.info",
            "data": grouped,
        }

        return self._cache.set("live-counters", payload)

    async def _fetch_init_data(self) -> dict[str, object]:
        init_url = f"{RTS_INIT_URL}?host=worldometers&time={int(time.time() * 1000)}&callback=jsoncallback"
        init_jsonp = await fetch_text(init_url)
        return parse_init_jsonp(init_jsonp)

    def _collect_rel_keys(self, homepage_html: str) -> list[str]:
        soup = BeautifulSoup(homepage_html, "html.parser")
        return [str(item.get("rel")) for item in soup.select(".rts-counter[rel]") if item.get("rel")]


def split_rel_key(rel_key: str) -> tuple[str, str | None]:
    if "/" not in rel_key:
        return rel_key, None

    base_key, action = rel_key.split("/", 1)
    return base_key, action


def q1(hostname: str, key_len: int = 2) -> str:
    parts = hostname.split(".")
    if len(parts) > key_len:
        parts = parts[len(parts) - key_len :]
    return ".".join(parts)


def hex_to_bytestring(hex_text: str) -> str:
    if len(hex_text) % 2 != 0:
        hex_text = f"0{hex_text}"
    return "".join(chr(int(hex_text[i : i + 2], 16)) for i in range(0, len(hex_text), 2))


def rc4_decrypt(key: str, cipher_text: str) -> str:
    state = list(range(256))
    j = 0
    key_bytes = [ord(char) for char in key]

    for i in range(256):
        j = (j + state[i] + key_bytes[i % len(key_bytes)]) % 256
        state[i], state[j] = state[j], state[i]

    i = 0
    j = 0
    result_chars: list[str] = []

    for char in cipher_text:
        i = (i + 1) % 256
        j = (j + state[i]) % 256
        state[i], state[j] = state[j], state[i]
        key_stream = state[(state[i] + state[j]) % 256]
        result_chars.append(chr(ord(char) ^ key_stream))

    return "".join(result_chars)


def decode_live_payload(encoded_hex: str, key: str) -> str:
    raw_cipher = hex_to_bytestring(encoded_hex)
    decrypted = rc4_decrypt(key, raw_cipher)
    percent_encoded = "".join(f"%{ord(char):02X}" for char in decrypted)
    return unquote(percent_encoded)


def parse_init_jsonp(jsonp_text: str) -> dict[str, object]:
    match = re.search(r"^[^(]+\((.*)\)\s*;?$", jsonp_text.strip(), re.S)
    if not match:
        raise ValueError("Unexpected JSONP payload for live counter init.")

    argument = match.group(1).strip()
    if len(argument) < 2 or argument[0] != argument[-1] or argument[0] not in {"'", '"'}:
        raise ValueError("Encoded live payload format is invalid.")

    encoded_payload = argument[1:-1]
    decoded_json = decode_live_payload(encoded_payload, q1("worldometers.info"))

    payload = json.loads(decoded_json)
    if not isinstance(payload, dict):
        raise ValueError("Decoded live payload is invalid.")

    return payload


def start_of_year_millis(timestamp_ms: float) -> float:
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    start = datetime(dt.year, 1, 1, tzinfo=timezone.utc)
    return start.timestamp() * 1000


def start_of_day_millis(timestamp_ms: float) -> float:
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    start = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
    return start.timestamp() * 1000


def date_constant_lookup(seconds_script: str) -> dict[str, float]:
    constants: dict[str, float] = {}
    pattern = r"var\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*new Date\((\d+)\)"
    for name, millis in re.findall(pattern, seconds_script):
        constants[name] = float(millis)
    return constants


def resolve_seconds_value(
    name: str,
    constants: dict[str, float],
    now_ms: float,
    now_server_ms: float,
    new_year_ms: float,
    new_year_server_ms: float,
    today_ms: float,
    today_server_ms: float,
) -> float:
    if name == "seconds_now":
        return round(now_ms) / 1000
    if name == "seconds_now_server":
        return round(now_server_ms) / 1000
    if name == "seconds_new_year":
        return round(new_year_ms) / 1000
    if name == "seconds_new_year_server":
        return round(new_year_server_ms) / 1000
    if name == "seconds_since_new_year":
        return round(now_ms - new_year_ms) / 1000
    if name == "seconds_since_new_year_server":
        return round(now_server_ms - new_year_server_ms) / 1000
    if name == "seconds_today":
        return (now_ms - today_ms) / 1000
    if name == "seconds_today_server":
        return (now_server_ms - today_server_ms) / 1000
    if name == "hours_now_server":
        hour = datetime.fromtimestamp(now_server_ms / 1000, tz=timezone.utc).hour
        return float((hour - 5) % 24)

    server_suffix = "_server"

    if name.startswith("seconds_since_"):
        base_name = name[len("seconds_since_") :]
        is_server = base_name.endswith(server_suffix)
        if is_server:
            base_name = base_name[: -len(server_suffix)]

        base_name = SECONDS_NAME_ALIASES.get(base_name, base_name)
        if base_name not in constants:
            raise ValueError(f"Unsupported seconds variable: {name}")

        reference_ms = constants[base_name]
        current_ms = now_server_ms if is_server else now_ms
        return round(current_ms - reference_ms) / 1000

    if name.startswith("seconds_"):
        base_name = name[len("seconds_") :]
        is_server = base_name.endswith(server_suffix)
        if is_server:
            base_name = base_name[: -len(server_suffix)]

        base_name = SECONDS_NAME_ALIASES.get(base_name, base_name)
        if base_name not in constants:
            raise ValueError(f"Unsupported seconds variable: {name}")

        reference_ms = constants[base_name]
        return round(reference_ms) / 1000

    raise ValueError(f"Unknown seconds variable: {name}")


def collect_formula_seconds_variables(counters: dict[str, object], rel_keys: list[str]) -> set[str]:
    needed: set[str] = set()

    for rel_key in rel_keys:
        base_key, action = split_rel_key(rel_key)
        counter = counters.get(base_key)
        if not isinstance(counter, dict):
            continue

        formula = select_counter_formula(counter, action)
        if formula is None:
            continue

        for var_name in re.findall(r"rts_seconds\.([a-zA-Z0-9_]+)", formula):
            needed.add(var_name)

    return needed


def build_seconds_context(init_data: dict[str, object], needed_variables: set[str]) -> dict[str, float]:
    seconds_script = str(init_data.get("seconds", ""))
    constants = date_constant_lookup(seconds_script)

    now_ms = time.time() * 1000
    now_server_ms = float(init_data.get("serverTime", now_ms))

    new_year_ms = start_of_year_millis(now_ms)
    new_year_server_ms = start_of_year_millis(now_server_ms)
    today_ms = start_of_day_millis(now_ms)
    today_server_ms = constants.get("todaysdate_server", start_of_day_millis(now_server_ms))

    values: dict[str, float] = {}
    for variable in needed_variables:
        values[variable] = resolve_seconds_value(
            variable,
            constants,
            now_ms,
            now_server_ms,
            new_year_ms,
            new_year_server_ms,
            today_ms,
            today_server_ms,
        )

    return values


def js_round(number: float) -> int:
    if number >= 0:
        return int(math.floor(number + 0.5))
    return int(math.ceil(number - 0.5))


def normalize_formula(formula: str) -> str:
    expression = formula.strip()
    if expression.startswith("return"):
        expression = expression[len("return") :].strip()
    if expression.endswith(";"):
        expression = expression[:-1]

    expression = expression.replace("Math.round", "round_js")
    expression = expression.replace("Math.pow", "pow")
    expression = re.sub(r"rts_seconds\.([a-zA-Z0-9_]+)", r"seconds_values['\1']", expression)
    return expression


def evaluate_formula(formula: str, seconds_values: dict[str, float]) -> int:
    expression = normalize_formula(formula)
    evaluator = SafeExpressionEvaluator(seconds_values)
    value = evaluator.evaluate(expression)
    return js_round(value)


def select_counter_formula(counter: dict[str, object], action: str | None) -> str | None:
    if action and f"{action}_formula" in counter:
        return str(counter[f"{action}_formula"])

    if "formula" in counter:
        return str(counter["formula"])

    if "today_formula" in counter:
        return str(counter["today_formula"])

    counter_types = counter.get("types")
    if isinstance(counter_types, list) and counter_types:
        first_type = str(counter_types[0])
        formula_key = f"{first_type}_formula"
        if formula_key in counter:
            return str(counter[formula_key])

    return None
