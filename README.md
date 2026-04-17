# worldometer-api

Lightweight Cloudflare Python Worker API that exposes data from worldometers.info.

This project exposes Worker routes for:

- Live counters
- Country codes
- Population data (current, historical, projected)
- Geography data

## Architecture

The codebase is split into single-responsibility modules under `src/worldometer_api`:

- `router.py`: HTTP route orchestration
- `service.py`: business-level API use cases
- `live_counters_service.py`: realtime counters decoding and evaluation
- `table_service.py`: table fetching and cache-aware retrieval
- `table_parser.py`: HTML table normalization/parsing
- `cache.py`: TTL cache implementation
- `openapi.py`: OpenAPI spec and docs page generator
- `http.py`: HTTP response helpers
- `config.py`: central constants and route mappings

## Requirements

- Node.js
- uv
- Cloudflare account

## Install

```bash
uv sync
```

## Local development

```bash
uv run pywrangler dev
```

## Deploy

```bash
uv run pywrangler deploy
```

## API routes

- GET `/` (OpenAPI HTML docs)
- GET `/docs` (OpenAPI HTML docs)
- GET `/api` (OpenAPI HTML docs)
- GET `/openapi.json`
- GET `/api/live`
- GET `/api/country-codes`
- GET `/api/population/countries`
- GET `/api/population/most-populous?period=current|past|future`
- GET `/api/population/largest-cities`
- GET `/api/population/by-region?period=current|past|future`
- GET `/api/population/by-year`
- GET `/api/population/projections`
- GET `/api/population/region/{region}?dataset=subregions|historical|forecast`
- GET `/api/geography/largest-countries`
- GET `/api/geography/world-countries`
- GET `/api/geography/region/{region}?dataset=countries|dependencies`

Supported `{region}` values:

- `asia`
- `africa`
- `europe`
- `latin-america`
- `northern-america`
- `oceania`

## Notes

- Responses are JSON.
- `/`, `/docs` and `/api` return Scalar HTML documentation.
- The worker applies a short in-memory cache to reduce upstream calls.
- Live counters are computed from the same real-time source used by worldometers.info.
