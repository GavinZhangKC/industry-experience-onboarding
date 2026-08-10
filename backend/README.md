# Sensory-Aware Route Planner — Backend

FastAPI backend covering BE-F1 to BE-F5. It runs locally with no AWS account,
Google key, or database, and uses the same services when deployed to Lambda.

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
  lib/               geo.py and interchangeable JSON/Aurora data stores
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
| `GET /health` | `lambda_handlers.health.handler` | provider and reference-data status |
| `POST /api/v1/routes` | `lambda_handlers.routes.handler` | `plan_routes()` → `score_route()` |
| `GET /api/v1/quiet-spaces` | `lambda_handlers.quiet_spaces.handler` | `find_quiet_spaces()` |
| `POST /api/v1/refuge-detour` | `lambda_handlers.refuge_detour.handler` | `plan_refuge_detour()` |

The endpoint adapters can also be configured as separate Lambda entry points
if the deployment later adds a routing layer in front of multiple Function
URLs. Shared response, request-id, validation-error, and safe error-envelope
handling lives in `lambda_handlers/common.py`.

No handler contains route generation, sensory scoring, distance calculations,
or data access logic. Configuration continues to come from environment
variables through `app.config.get_settings()`.

## Reference data: local JSON or Aurora

The service layer consumes one storage-neutral contract. Local development
uses the checked-in JSON datasets by default:

```text
DATA_BACKEND=json
```

For AWS, set `DATA_BACKEND=aurora` and provide `AWS_REGION`,
`DB_CLUSTER_ARN`, `DB_SECRET_ARN`, and `DB_NAME`. The Aurora adapter is
read-only and uses the RDS Data API; F1/F2 and F3 require no business-logic
changes when switching backends. Credentials and ARNs are never hard-coded.

The root-level Node scripts are F4 ingestion utilities only. They populate the
same Aurora schema and are not a second HTTP backend:

```bash
npm run ingest:pedestrian
npm run ingest:refuges
```

For an existing Aurora database, apply
`migrations/001_ingestion_idempotency.sql` through the team's normal database
migration process before running the updated scripts. Fresh databases can use
the current `schema.sql` directly. The scripts use source-keyed upserts, so
rerunning them updates known locations and readings instead of duplicating
them.

## AWS deployment

The root `template.yaml` packages `backend/` as a Python Lambda and exposes the
shared handler through a Lambda Function URL. Supply the existing Aurora ARNs
as deployment parameters rather than adding them to source control:

```bash
sam build
sam deploy --guided
```

During the guided deployment, provide `DbClusterArn`, `DbSecretArn`,
`DbName`, and the deployed frontend origin. Keep `MapsProvider=mock` until the
separate Google Maps integration is ready.

### Vercel alternative

Vercel imports `backend/main.py` as the FastAPI ASGI application. The existing
AWS Lambda handlers and SAM template remain available; both adapters use the
same API routes and services. Deployment settings and the AWS IAM policy are
documented in the repository's `VERCEL_DEPLOYMENT.md`.

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
| Lambda Function URL adapter | `lambda_handlers/`, `template.yaml` | Implemented; cloud deployment still requires AWS parameters |

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

## Still to complete

- Deploy the SAM stack with the team's Aurora ARNs and frontend origin.
- Turn the Node ingestion scripts into scheduled/operated AWS jobs if automatic
  refresh is required; today they are manually invoked utilities.
- Add pagination before using ingestion at production scale; the current source
  requests are limited to 100 records.
- Replace the hand-seeded JSON data before treating JSON mode as production
  data; it remains suitable for the current Vercel demo deployment.
- Implement a real live "quiet now" signal for US2.2; the current description
  field is static reference information.
- Complete and enable the separate Google Maps provider configuration.
- Add authentication only if the product introduces user accounts.
