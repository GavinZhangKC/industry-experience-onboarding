const test = require('node:test');
const assert = require('node:assert/strict');

const { cleanSensorRecord, cleanReadingRecord } = require('../ingest');
const { cleanRefugeRecord } = require('../ingest-refuge');

test('cleanSensorRecord normalizes a valid Melbourne sensor', () => {
  const result = cleanSensorRecord({
    location_id: 42,
    sensor_description: ' Test Sensor ',
    latitude: '-37.81',
    longitude: '144.96',
    status: 'A'
  });

  assert.equal(result.valid, true);
  assert.deepEqual(result.cleaned, {
    sensor_id: '42',
    name: 'Test Sensor',
    latitude: -37.81,
    longitude: 144.96,
    status: 'a'
  });
});

test('cleanReadingRecord rejects negative pedestrian counts', () => {
  const result = cleanReadingRecord({
    location_id: 42,
    sensing_datetime: '2026-08-09T01:00:00Z',
    total_of_directions: -1
  });

  assert.equal(result.valid, false);
  assert.ok(result.issues.includes('negative count — invalid'));
});

test('cleanRefugeRecord keeps supported refuge categories', () => {
  const result = cleanRefugeRecord({
    feature_name: 'City Library',
    sub_theme: 'Public Buildings',
    co_ordinates: { lat: -37.81, lon: 144.96 }
  });

  assert.equal(result.valid, true);
  assert.equal(result.cleaned.type, 'indoor');
  assert.equal(result.cleaned.source_key, 'refuge:indoor:city library');
});

test('cleaning rejects partially numeric coordinates and counts', () => {
  const sensor = cleanSensorRecord({
    location_id: 42,
    sensor_description: 'Test Sensor',
    latitude: '-37.81abc',
    longitude: '144.96',
  });
  const reading = cleanReadingRecord({
    location_id: 42,
    sensing_datetime: '2026-08-09T01:00:00Z',
    total_of_directions: '12.5',
  });

  assert.equal(sensor.valid, false);
  assert.ok(sensor.issues.includes('latitude not numeric'));
  assert.equal(reading.valid, false);
  assert.ok(reading.issues.includes('count not numeric'));
});