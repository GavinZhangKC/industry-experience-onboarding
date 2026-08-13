// Ingests the "Pedestrian Counting System — Monthly Counts per Hour" dataset —
// previously listed in the Data Management Plan as a planned source but never
// actually wired up. This is what makes US 1.3 (threshold-based rerouting) and
// US 2.2 (predictive alerts) possible: without genuine historical data, there
// is nothing to compare "right now" against except a flat 28-day average.
//
// Reuses cleanReadingRecord from ingest.js rather than duplicating the
// cleaning rules — same bounding-box/type-coercion/negative-count logic
// applies here, since it's the same underlying measurement (a pedestrian
// count at a sensor, at a timestamp), just from a different endpoint.
//
// IMPORTANT — verify field names before your first real run:
// This dataset's schema page renders via client-side JS, so its exact field
// names couldn't be confirmed by automated fetch. The names below
// (sensor_id, date_time, hourly_counts) match City of Melbourne's
// well-documented, widely-published version of this dataset. Run this first:
//   node -e "fetch('https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/pedestrian-counting-system-monthly-counts-per-hour/records?limit=1').then(r=>r.json()).then(d=>console.log(JSON.stringify(d.results[0],null,2)))"
// and compare the printed field names against FIELD_MAP below. If they
// differ, this script will fail fast and tell you exactly which field is
// missing, rather than silently reporting "0 inserted".

const fetch = require('node-fetch');
const { query } = require('./db');
const { cleanReadingRecord } = require('./ingest');

const DATASET_URL =
  'https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/pedestrian-counting-system-monthly-counts-per-hour/records';

// Maps this dataset's field names onto the shape cleanReadingRecord() expects
// (which was written against the past-hour-counts-per-minute dataset's
// field names: location_id, sensing_datetime, total_of_directions).
const FIELD_MAP = {
  sensor_id: 'sensor_id',
  date_time: 'date_time',
  hourly_counts: 'hourly_counts'
};

function assertExpectedFields(sampleRecord) {
  const missing = Object.values(FIELD_MAP).filter(f => !(f in sampleRecord));
  if (missing.length > 0) {
    throw new Error(
      `Monthly Counts per Hour dataset is missing expected field(s): ${missing.join(', ')}. ` +
      `Actual fields present: ${Object.keys(sampleRecord).join(', ')}. ` +
      `Update FIELD_MAP in ingest-hourly-trends.js to match, then re-run.`
    );
  }
}

function toReadingShape(record) {
  return {
    location_id: record[FIELD_MAP.sensor_id],
    sensing_datetime: record[FIELD_MAP.date_time],
    total_of_directions: record[FIELD_MAP.hourly_counts]
  };
}

async function ingestHourlyTrends({ months = 3, limitPerPage = 100 } = {}) {
  const since = new Date();
  since.setMonth(since.getMonth() - months);
  const whereClause = `date_time >= date'${since.toISOString().slice(0, 10)}'`;

  const res = await fetch(
    `${DATASET_URL}?limit=${limitPerPage}&where=${encodeURIComponent(whereClause)}`
  );
  const data = await res.json();
  if (!res.ok || !Array.isArray(data.results)) {
    throw new Error(`Monthly counts source returned HTTP ${res.status}`);
  }
  console.log(`Fetched ${data.results.length} raw historical reading records (last ${months} month(s))`);

  if (data.results.length > 0) {
    assertExpectedFields(data.results[0]);
  }

  let inserted = 0, rejected = 0, skippedUnknownSensor = 0, duplicates = 0;
  const rejectionLog = [];
  const seen = new Set();

  for (const raw of data.results) {
    const record = toReadingShape(raw);
    const dedupeKey = `${record.location_id}|${record.sensing_datetime}`;
    if (seen.has(dedupeKey)) {
      duplicates++;
      continue;
    }
    seen.add(dedupeKey);

    const { valid, issues, cleaned } = cleanReadingRecord(record);
    if (!valid) {
      rejected++;
      rejectionLog.push({ sensor_id: record.location_id, issues });
      continue;
    }

    try {
      // ON CONFLICT DO NOTHING would need a unique constraint on
      // (sensor_id, recorded_at), which the current schema doesn't have —
      // see migrations/001_ingestion_idempotency.sql on the codebase-hardening
      // branch for exactly that fix. Until it's merged, re-running this
      // script over the same historical window will duplicate rows.
      await query(
        `INSERT INTO pedestrian_reading (sensor_id, count, recorded_at) VALUES (:sid, :count, :recorded_at::timestamptz)`,
        [
          { name: 'sid', value: { stringValue: cleaned.sensor_id } },
          { name: 'count', value: { longValue: cleaned.count } },
          { name: 'recorded_at', value: { stringValue: cleaned.recorded_at } }
        ]
      );
      inserted++;
    } catch (err) {
      if (err.name === 'BadRequestException' && /foreign key/i.test(err.message)) {
        skippedUnknownSensor++;
        continue;
      }
      throw err;
    }
  }

  console.log(
    `Historical trend report: ${inserted} inserted, ${rejected} rejected, ` +
    `${duplicates} duplicates skipped, ${skippedUnknownSensor} skipped (unknown sensor)`
  );
  if (rejectionLog.length) console.log('Rejected records:', JSON.stringify(rejectionLog.slice(0, 20), null, 2));

  return { inserted, rejected, duplicates, skippedUnknownSensor };
}

if (require.main === module) {
  ingestHourlyTrends().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}

module.exports = { ingestHourlyTrends, assertExpectedFields, toReadingShape };
