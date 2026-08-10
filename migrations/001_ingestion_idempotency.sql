-- Apply once to databases created before source-keyed ingestion existed.
-- Existing locations remain valid; new ingestion records receive a source_key
-- and are updated in place on subsequent runs.

ALTER TABLE location ADD COLUMN IF NOT EXISTS source_key text;
ALTER TABLE location
  ADD CONSTRAINT location_source_key_unique UNIQUE (source_key);

-- A source can publish the same minute's reading more than once. Keep the
-- newest row before protecting that natural key.
DELETE FROM pedestrian_reading
WHERE reading_id IN (
  SELECT reading_id
  FROM (
    SELECT
      reading_id,
      ROW_NUMBER() OVER (
        PARTITION BY sensor_id, recorded_at
        ORDER BY fetched_at DESC NULLS LAST, reading_id DESC
      ) AS row_number
    FROM pedestrian_reading
  ) duplicates
  WHERE row_number > 1
);

ALTER TABLE pedestrian_reading
  ADD CONSTRAINT pedestrian_reading_sensor_recorded_at_unique
  UNIQUE (sensor_id, recorded_at);

ALTER TABLE refuge
  ADD CONSTRAINT refuge_location_id_unique UNIQUE (location_id);