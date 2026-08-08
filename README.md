# Sensory-Aware Route Planner

A university team project (Monash FIT5120). Helps neurodivergent,
sensory-sensitive commuters walk through Melbourne's CBD by showing which
routes are calm and where nearby quiet spaces are.

- `backend/` — FastAPI/Lambda service (routing, sensory scoring, quiet-space search)
- `frontend/` — React + Vite + TypeScript client (map, journey input, results)
- Root Node scripts — Aurora ingestion utilities, not a second HTTP server

## Run both together

Two terminals, both from the repo root.

**Terminal 1 — backend** (`http://127.0.0.1:8000`):

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

**Terminal 2 — frontend** (`http://localhost:5173`):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. No further configuration is needed — the
backend runs in mock mode by default (`MAPS_PROVIDER=mock` in
`backend/.env`), so no Google Maps key, database, or AWS account is
required, and the backend's CORS allow-list already includes
`http://localhost:5173`.

To point the frontend at a backend running somewhere else, copy
`frontend/.env.example` to `frontend/.env.local` and set
`VITE_API_BASE_URL`.

## What each side does

The backend is documented in [backend/README.md](backend/README.md) —
endpoints, the mock mapping provider, error envelope, and the sensory
scoring model.

The frontend covers four functionalities against the live API contract:

- **FE-F1 — Journey input.** Pick an origin and destination from a fixed
  list of Melbourne landmarks, or click a point on the map. (The backend
  takes coordinates only; there's no geocoding endpoint yet — see
  `frontend/src/constants/landmarks.ts` for the stand-in and TODO.)
- **FE-F2 — Route comparison.** Every alternative route is drawn on the
  map and listed as a card with duration, distance, a sensory badge
  (Low/Medium/High, never colour-only), and the plain-language explanation.
- **FE-F3 — Quiet space search.** A persistent "Find quiet space" bar,
  reachable from any screen, using geolocation or the current map centre.
- **FE-F4 — Quiet space results.** Markers plus a list; selecting one opens
  a detail panel. An empty result offers to expand the search radius
  (500 m → 1000 m → 2000 m).

No location data (origin, destination, or resolved geolocation) is ever
written to `localStorage` or persisted anywhere in the frontend.

## Accessibility

Built for people with sensory sensitivities and invisible disabilities —
these are requirements, not nice-to-haves:

- Sensory level is always text + a distinct shape/glyph, never colour alone.
- Muted, calm palette; contrast verified against WCAG AA.
- Fully keyboard operable, including map panning/zoom (arrow keys, `+`/`-`)
  and route/quiet-space selection. The route and quiet-space lists are the
  non-visual equivalent of the map — everything the map shows is also there
  as text.
- `prefers-reduced-motion` honoured; no animation on state changes by
  default, no flashing or autoplay anywhere.

## Tests

```bash
cd backend && python -m pytest tests -q
cd .. && npm ci && npm test
```

The frontend has no automated test suite yet; verify changes with
`npm run build` (typecheck) and a manual pass in the browser.
