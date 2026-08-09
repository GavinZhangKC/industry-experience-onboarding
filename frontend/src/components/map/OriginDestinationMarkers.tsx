import { Marker, Tooltip } from "react-leaflet";
import type { Coordinate } from "../../api/types";
import { destinationIcon, originIcon } from "./icons";

interface OriginDestinationMarkersProps {
  origin: Coordinate | null;
  destination: Coordinate | null;
}

export function OriginDestinationMarkers({ origin, destination }: OriginDestinationMarkersProps) {
  return (
    <>
      {origin && (
        <Marker position={[origin.lat, origin.lng]} icon={originIcon} alt="Origin">
          <Tooltip>Origin</Tooltip>
        </Marker>
      )}
      {destination && (
        <Marker position={[destination.lat, destination.lng]} icon={destinationIcon} alt="Destination">
          <Tooltip>Destination</Tooltip>
        </Marker>
      )}
    </>
  );
}
