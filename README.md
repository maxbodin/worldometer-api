# worldometer-api

Lightweight Cloudflare Python Worker API that exposes data from worldometers.info.

This project exposes Worker routes for:

- Live counters
- Country codes
- Population data (current, historical, projected)
- Geography data
- Energy data
- Water data
- GDP data
- Food & Agriculture data
- GHG emissions data
- Maps data

## Architecture

The codebase is split into single-responsibility modules under `src/worldometer_api`:

- `router.py`: HTTP route orchestration
- `service.py`: business-level API use cases
- `live_counters_service.py`: realtime counters decoding and evaluation
- `table_service.py`: table fetching and cache-aware retrieval
- `table_parser.py`: HTML table normalization/parsing
- `energy_parser.py`: country energy summary parsing
- `water_parser.py`: country water summary parsing
- `food_agriculture_parser.py`: country food/agriculture section parsing
- `maps_parser.py`: country maps parsing
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

Or use:

```bash
make install
```

## Local development

```bash
uv run pywrangler dev
```

## Deploy

```bash
uv run pywrangler deploy
```

## End-to-end tests

The e2e suite exercises every public API route with real HTTP calls and real upstream data.

```bash
uv run pytest tests/e2e -m e2e
```

Optional environment variables:

- `E2E_BASE_URL` (default: `http://127.0.0.1:8787`)
- `E2E_START_SERVER` (`1`/`0`, default: `1`)

## API routes

- GET `/` (OpenAPI HTML docs)
- GET `/docs` (OpenAPI HTML docs)
- GET `/api` (OpenAPI HTML docs)
- GET `/openapi.json`
- GET `/live`
- GET `/population/country-codes`
- GET `/population/countries`
- GET `/population/most-populous?period=current|past|future`
- GET `/population/largest-cities`
- GET `/population/by-region?period=current|past|future`
- GET `/population/by-year`
- GET `/population/projections`
- GET `/population/region/{region}?dataset=subregions|historical|forecast`
- GET `/population/country/{countryIdentifier}`
- GET `/geography/largest-countries`
- GET `/geography/world-countries`
- GET `/geography/region/{region}?dataset=countries|dependencies`
- GET `/energy`
- GET `/energy/country/{countryIdentifier}?dataset=all|energy|electricity|gas|oil|coal`
- GET `/water`
- GET `/water/country/{countryIdentifier}`
- GET `/gdp?dataset=by-country|per-capita`
- GET `/gdp/by-country`
- GET `/gdp/per-capita`
- GET `/gdp/country/{countryIdentifier}`
- GET `/food-agriculture?dataset=undernourishment|forest|cropland|pesticides`
- GET `/food-agriculture/undernourishment`
- GET `/food-agriculture/forest`
- GET `/food-agriculture/cropland`
- GET `/food-agriculture/pesticides`
- GET `/food-agriculture/country/{countryIdentifier}`
- GET `/ghg-emissions`
- GET `/ghg-emissions/greenhouse`
- GET `/ghg-emissions/greenhouse/by-country`
- GET `/ghg-emissions/greenhouse/by-year`
- GET `/ghg-emissions/greenhouse/per-capita`
- GET `/ghg-emissions/co2`
- GET `/ghg-emissions/co2/by-country`
- GET `/ghg-emissions/co2/by-year`
- GET `/ghg-emissions/co2/per-capita`
- GET `/ghg-emissions/country/{countryIdentifier}?dataset=all|greenhouse|co2`
- GET `/maps`
- GET `/maps/country/{countryIdentifier}`
- GET `/maps/physical/{countryIdentifier}`
- GET `/maps/political/{countryIdentifier}`
- GET `/maps/road/{countryIdentifier}`
- GET `/maps/locator/{countryIdentifier}`

`{countryIdentifier}` accepts a country name, 2-letter ISO alpha code, or 3-letter ISO alpha code.

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
