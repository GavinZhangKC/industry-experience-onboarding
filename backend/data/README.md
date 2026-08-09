# Reference data (BE-F4)

Both files use the same record shape, so either can be moved to Supabase or
Postgres without touching the services that read them.

| Field | Notes |
|---|---|
| `id` | Stable slug, unique within the file |
| `name` | What the user sees |
| `type` | Category, used for filtering and for the explanation text |
| `lat`, `lng` | Decimal degrees, WGS84 |
| `weight` | `busy_areas.json` only. 1–5, how strongly it pushes the sensory score up |
| `description` | `quiet_spaces.json` only. One static sentence, e.g. "Open green space with riverside seating". Not live occupancy/noise data — see TODO below |

## Status

**These are hand-seeded placeholder records, not open data.** They exist so the
scoring engine and the quiet-space search return sensible results before the
City of Melbourne ingest is built. Before submission, replace them with:

- `busy_areas.json` → City of Melbourne Pedestrian Counting System sensor
  locations, with `weight` derived from each sensor's 4-week rolling average
  rather than assigned by hand.
- `quiet_spaces.json` → City of Melbourne open space and public facility
  datasets.

Keeping the record shape identical means that swap is a data change, not a
code change.

## TODO: live status (US2.2)

`quiet_spaces.json`'s `description` is a static, hand-written sentence per
record — not "quiet now" / occupancy data. A real live status needs a join
against the City of Melbourne Pedestrian Counting System sensor feed (the
same source `busy_areas.json` will eventually derive `weight` from). That's
a later iteration; don't fake a live signal out of this field in the
meantime.
