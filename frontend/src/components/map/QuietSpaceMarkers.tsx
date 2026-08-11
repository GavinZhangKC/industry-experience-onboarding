import { Circle, CircleMarker, Marker, Tooltip } from "react-leaflet";
import type { QuietSpace } from "../../api/types";
import { quietSpaceIcon, quietSpaceSelectedIcon } from "./icons";

interface QuietSpaceMarkersProps {
  spaces: QuietSpace[];
  selectedId: string | null;
  onSelect: (space: QuietSpace) => void;
  searchCenter?: { lat: number; lng: number } | null;
  radiusM?: number;
  searchCenterLabel?: string;
}

export function QuietSpaceMarkers({
  spaces,
  selectedId,
  onSelect,
  searchCenter,
  radiusM,
  searchCenterLabel = "Search location",
}: QuietSpaceMarkersProps) {
  return (
    <>
      {searchCenter && radiusM && (
        <>
          <Circle
            center={[
              searchCenter.lat,
              searchCenter.lng,
            ]}
            radius={radiusM}
            pathOptions={{
              color: "#174f9e",
              weight: 3,
              opacity: 0.9,
              fillColor: "#5b8fd6",
              fillOpacity: 0.16,
            }}
          />
          <CircleMarker
            center={[searchCenter.lat, searchCenter.lng]}
            radius={8}
            pathOptions={{ color: "#ffffff", weight: 3, fillColor: "#174f9e", fillOpacity: 1 }}
          >
            <Tooltip permanent direction="top" offset={[0, -8]}>
              {searchCenterLabel}
            </Tooltip>
          </CircleMarker>
        </>
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
