import type { SensoryLevel } from "../api/types";

// Level must never be conveyed by colour alone: each entry pairs a colour
// with a distinct shape/glyph and a text label so the badge still reads
// correctly with colour vision deficiency or colour disabled entirely.
export interface SensoryLevelPresentation {
  label: string;
  glyph: string;
  shapeClass: string;
}

export const SENSORY_LEVEL_PRESENTATION: Record<SensoryLevel, SensoryLevelPresentation> = {
  low: { label: "Low", glyph: "●", shapeClass: "shape-circle" },
  medium: { label: "Medium", glyph: "▲", shapeClass: "shape-triangle" },
  high: { label: "High", glyph: "■", shapeClass: "shape-square" },
};
