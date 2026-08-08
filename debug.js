require('dotenv').config();
const fetch = require('node-fetch');

async function testDirections() {
  const origin = '-37.8183,144.9671';      // Flinders Street Station
  const destination = '-37.8136,144.9631'; // Bourke Street Mall
  const url = `https://maps.googleapis.com/maps/api/directions/json?origin=${origin}&destination=${destination}&mode=walking&alternatives=true&key=${process.env.GOOGLE_MAPS_API_KEY}`;

  const res = await fetch(url);
  const data = await res.json();

  console.log('STATUS:', data.status);
  console.log('NUMBER OF ROUTES:', data.routes?.length);
  console.log('FIRST ROUTE, FIRST STEP:', JSON.stringify(data.routes?.[0]?.legs?.[0]?.steps?.[0], null, 2));
}

testDirections();
