import { Circle, Marker, Tooltip } from "react-leaflet";
import type { QuietSpace } from "../../api/types";
import { quietSpaceIcon, quietSpaceSelectedIcon } from "./icons";

interface QuietSpaceMarkersProps {
  spaces: QuietSpace[];
  selectedId: string | null;
  onSelect: (space: QuietSpace) => void;
  searchCenter?: { lat: number; lng: number } | null;
  radiusM?: number;
}

export function QuietSpaceMarkers({ spaces, selectedId, onSelect, searchCenter, radiusM }: QuietSpaceMarkersProps) {
  return (
    <>
      {searchCenter && radiusM && (
        <Circle
          center={[searchCenter.lat, searchCenter.lng]}
          radius={radiusM}
          pathOptions={{ color: "#2f6b63", weight: 1, opacity: 0.5, fillOpacity: 0.05 }}
        />
      )}
      {spaces.map((space) => (
        <Marker
          key={space.id}
          position={[space.lat, space.lng]}
          icon={space.id === selectedId ? quietSpaceSelectedIcon : quietSpaceIcon}
          alt={`Quiet space: ${space.name}`}
          eventHandlers={{ click: () => onSelect(space) }}
        >
          <Tooltip>{space.name}</Tooltip>
        </Marker>
      ))}
    </>
  );
}
