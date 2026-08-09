import type { Coordinate } from "../api/types";

// STAND-IN for real place search. The backend takes coordinates only — there
// is no geocoding or autocomplete endpoint. This fixed list lets a user pick
// an origin/destination without typing an address.
//
// TODO: once a backend geocoding endpoint exists, replace this list (and the
// "pick a landmark" mode in LocationSelect) with real place search.
export interface Landmark {
  id: string;
  name: string;
  coordinate: Coordinate;
}

export const MELBOURNE_LANDMARKS: Landmark[] = [
  { id: "flinders-street-station", name: "Flinders Street Station", coordinate: { lat: -37.8183, lng: 144.9671 } },
  { id: "state-library", name: "State Library Victoria", coordinate: { lat: -37.8098, lng: 144.9652 } },
  { id: "federation-square", name: "Federation Square", coordinate: { lat: -37.8179, lng: 144.969 } },
  { id: "queen-victoria-market", name: "Queen Victoria Market", coordinate: { lat: -37.8076, lng: 144.9568 } },
  { id: "carlton-gardens", name: "Carlton Gardens", coordinate: { lat: -37.8036, lng: 144.9707 } },
  { id: "flagstaff-gardens", name: "Flagstaff Gardens", coordinate: { lat: -37.811, lng: 144.954 } },
  { id: "treasury-gardens", name: "Treasury Gardens", coordinate: { lat: -37.814, lng: 144.9737 } },
  { id: "southern-cross-station", name: "Southern Cross Station", coordinate: { lat: -37.8183, lng: 144.9524 } },
  { id: "melbourne-central", name: "Melbourne Central", coordinate: { lat: -37.81, lng: 144.9633 } },
  { id: "birrarung-marr", name: "Birrarung Marr", coordinate: { lat: -37.8188, lng: 144.9714 } },
];
