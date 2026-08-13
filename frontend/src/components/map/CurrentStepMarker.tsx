import { Marker, Tooltip } from "react-leaflet";
import type { RouteStep } from "../../api/types";
import { decodePolyline } from "../../utils/polyline";
import { navigationPositionIcon } from "./icons";

interface CurrentStepMarkerProps {
  step: RouteStep;
}

// Placed at the current step's starting point, not tracked from real
// geolocation — this reflects which step you've manually advanced to, not
// your actual GPS position. See RouteNavigation's own comment for the same
// honesty note about what this feature is and isn't.
export function CurrentStepMarker({ step }: CurrentStepMarkerProps) {
  const points = decodePolyline(step.polyline);
  if (points.length === 0) return null;
  const [lat, lng] = points[0];

  return (
    <Marker position={[lat, lng]} icon={navigationPositionIcon} alt="Current step">
      <Tooltip>{step.instruction}</Tooltip>
    </Marker>
  );
}
