import re
from typing import Any

from bs4 import BeautifulSoup


def parse_energy_country_summary(html: str) -> list[dict[str, Any]]:
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)

    consumed_match = re.search(
        r"consumed\s+([\d,]+)\s*BTU.*?represents\s+([\d.]+%)\s+of global energy consumption.*?"
        r"produced\s+([\d,]+)\s*BTU.*?covering\s+([\d.]+%)",
        text,
        re.IGNORECASE,
    )

    if consumed_match is None:
        return []

    non_renewable_match = re.search(
        r"Non Renewable \(Fossil Fuels\)\s+Energy Consumption\s+([\d.]+%)\s+([\d,]+)\s*BTU",
        text,
        re.IGNORECASE,
    )
    renewable_match = re.search(
        r"Renewable and Nuclear\s+Energy Consumption\s+([\d.]+%)\s+([\d,]+)\s*BTU",
        text,
        re.IGNORECASE,
    )
    oil_match = re.search(r"Oil\s*:\s*([\d,]+)\s*BTU\s*\(([\d.]+%)\)", text, re.IGNORECASE)
    gas_match = re.search(r"Gas\s*:\s*([\d,]+)\s*BTU\s*\(([\d.]+%)\)", text, re.IGNORECASE)
    coal_match = re.search(r"Coal\s*:\s*([\d,]+)\s*BTU\s*\(([\d.]+%)\)", text, re.IGNORECASE)

    row: dict[str, Any] = {
        "total_energy_consumed_btu": consumed_match.group(1),
        "global_energy_share": consumed_match.group(2),
        "total_energy_produced_btu": consumed_match.group(3),
        "self_sufficiency_share": consumed_match.group(4),
    }

    if non_renewable_match is not None:
        row["non_renewable_share"] = non_renewable_match.group(1)
        row["non_renewable_btu"] = non_renewable_match.group(2)

    if renewable_match is not None:
        row["renewable_and_nuclear_share"] = renewable_match.group(1)
        row["renewable_and_nuclear_btu"] = renewable_match.group(2)

    if oil_match is not None:
        row["oil_btu"] = oil_match.group(1)
        row["oil_share"] = oil_match.group(2)

    if gas_match is not None:
        row["gas_btu"] = gas_match.group(1)
        row["gas_share"] = gas_match.group(2)

    if coal_match is not None:
        row["coal_btu"] = coal_match.group(1)
        row["coal_share"] = coal_match.group(2)

    return [row]
