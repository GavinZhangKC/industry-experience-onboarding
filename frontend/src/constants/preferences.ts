export interface PreferenceState {
  avoidNoise: boolean;
  avoidCrowds: boolean;
  avoidConstruction: boolean;
  avoidMajorEvents: boolean;
}

export const DEFAULT_PREFERENCES: PreferenceState = {
  avoidNoise: true,
  avoidCrowds: true,
  avoidConstruction: true,
  avoidMajorEvents: true,
};
