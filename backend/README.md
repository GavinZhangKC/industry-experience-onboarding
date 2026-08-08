# Sensory-Aware Route Planner — Backend

FastAPI backend covering BE-F1 to BE-F5. Runs locally with no AWS account, no
Google key and no database.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Interactive docs at http://127.0.0.1:8000/docs

```bash
curl http://127.0.0.1:8000/health
```

## Endpoints

| Method | Path | Covers |
|---|---|---|
| `GET` | `/health` | Liveness, provider name, record counts |
| `POST` | `/api/v1/routes` | BE-F1 + BE-F2 |
| `GET` | `/api/v1/quiet-spaces` | BE-F3 — Refuge Finder search |
| `POST` | `/api/v1/refuge-detour` | BE-F3 (AC5) — detour to a refuge and back onto the original route |

```bash
curl -X POST http://127.0.0.1:8000/api/v1/routes \
  -H 'Content-Type: application/json' \
  -d '{"origin":{"lat":-37.8113,"lng":144.9541},
       "destination":{"lat":-37.8140,"lng":144.9737},
       "alternatives":3}'

# radius_m defaults to DEFAULT_RADIUS_METRES (800). category is optional:
# green_space | indoor, omitted means all.
curl 'http://127.0.0.1:8000/api/v1/quiet-spaces?lat=-37.8140&lng=144.9700&category=green_space'

curl -X POST http://127.0.0.1:8000/api/v1/refuge-detour \
  -H 'Content-Type: application/json' \
  -d '{"current":{"lat":-37.8113,"lng":144.9541},
       "refuge":{"lat":-37.8140,"lng":144.9737},
       "destination":{"lat":-37.8102,"lng":144.9628}}'
```

## Layout

```
app/
  main.py            FastAPI app — the ONLY file that knows about FastAPI
  config.py          Settings from environment (BE-F5)
  schemas.py         Request/response validation (BE-F5)
  errors.py          One error type per failure mode (BE-F5)
  api/               Thin HTTP handlers
  services/          Business logic — plain functions, no framework
    route_service.py     BE-F1 orchestration
    scoring_service.py   BE-F2
    refuge_service.py    BE-F3
  clients/           External providers (mock + Google)
  lib/               geo.py (pure maths), data_store.py (BE-F4)
  middleware/        Rate limiting, request ids (BE-F5)
data/                Seed datasets — see data/README.md
tests/               pytest
```

## The mock mapping provider

`MAPS_PROVIDER=mock` (the default) generates plausible alternative walking
routes with real encoded polylines and no external call. The frontend can be
built and demoed against it before anyone has a billable Google key. Switch to
`MAPS_PROVIDER=google` plus `GOOGLE_MAPS_API_KEY` and nothing else changes —
the response shape is identical.

## Lambda Function URL handlers

The AWS adapter layer is separate from both FastAPI and the services. Local
development continues to use `uvicorn app.main:app`, while a Lambda Function
URL can use this shared handler entry point:

```text
lambda_handlers.handler.handler
```

It preserves the existing paths and dispatches them to thin endpoint adapters:

| Method and path | Adapter | Service flow |
|---|---|---|
| `POST /api/v1/routes` | `lambda_handlers.routes.handler` | `plan_routes()` → `score_route()` |
| `GET /api/v1/quiet-spaces` | `lambda_handlers.quiet_spaces.handler` | `find_quiet_spaces()` |

The endpoint adapters can also be configured as separate Lambda entry points
if the deployment later adds a routing layer in front of multiple Function
URLs. Shared response, request-id, validation-error, and safe error-envelope
handling lives in `lambda_handlers/common.py`.

No handler contains route generation, sensory scoring, distance calculations,
or data access logic. Configuration continues to come from environment
variables through `app.config.get_settings()`.

## Security notes (BE-F5)

| Control | Where | Status |
|---|---|---|
| Keys in environment only | `config.py`, `clients/maps_client.py` | Done |
| Key never reaches frontend | All provider calls are server-side | Done |
| Request validation | `schemas.py` + service-area guard | Done |
| CORS allow-list | `main.py` | Done, add the deployed origin before release |
| Rate limiting | `middleware/rate_limit.py` | Done, see caveat below |
| Upstream + data error handling | `errors.py`, `clients/`, `lib/data_store.py` | Done |
| Consistent error envelope | `main.py` | Done |
| Deploy | — | Not started |

Every error returns the same shape, so the frontend switches on `error.code`
and never parses message text:

```json
{"error": {"code": "out_of_service_area",
           "message": "That location is outside the area this app covers.",
           "request_id": "a09553a2d5b6"}}
```

Unexpected exceptions are logged in full and returned as a generic 500. Stack
traces and library internals never appear in a response.

### Rate limiting caveat

The counter lives in process memory. Behind multiple workers — or on Lambda,
where each concurrent execution has its own memory — each instance counts
separately, so the effective limit multiplies by the number of instances. It is
adequate for the MVP and a demo. Beyond that the counter needs a shared store
(Redis) or the limit needs to move to the edge (API Gateway usage plans, or WAF
rate-based rules). Worth stating plainly rather than claiming edge-level
protection that isn't there.

`/api/v1/refuge-detour` makes two upstream mapping calls per request instead of
one, so it counts double against that same shared limit (`PATH_WEIGHTS` in
`app/middleware/rate_limit.py`) rather than getting its own separate counter —
a second counter would let it double the real request volume before either
limit trips.

## Tuning the sensory score

In `.env`:

- `PROXIMITY_METRES` (120) — how close a busy area must be to count
- `LOW_THRESHOLD` (33) and `MEDIUM_THRESHOLD` (66) — the band boundaries

Distance matters as well as count, so a route passing two busy areas at the
edge of the radius can score lower than one passing a single area very close.
That is intended, but it can read oddly next to the explanation text — worth a
look once real sensor data replaces the seed file.

## Tests

```bash
python3 -m pytest tests -q
```

`test_scoring.py` includes a test asserting the level and the explanation are
always derived from the same findings — that is US1.1 acceptance criterion 4
enforced in code rather than by convention.

## Not built yet

- Persistence (BE-F4 uses JSON files by design for the MVP)
- **Real City of Melbourne open-data ingest for `quiet_spaces.json` (AC6).**
  `data/quiet_spaces.json` is a hand-seeded placeholder file, not a live pull
  from the open dataset — AC6 ("refuge locations are pulled live from the open
  dataset, not hard-coded") is **not satisfied** by the current implementation.
  Satisfying it needs a `scripts/ingest_quiet_spaces.py` that fetches and maps
  the City of Melbourne open space / public facility datasets on a schedule,
  not per-request. See `data/README.md` for the same gap on `busy_areas.json`.
- Live "quiet now" status (US2.2) — see the TODO on `QuietSpace.description`
  in `app/schemas.py`
- Authentication (no user accounts in this iteration)
- Deployment config
