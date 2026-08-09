import { MapContainer, TileLayer, useMap, useMapEvents } from "react-leaflet";
import type { LatLngTuple } from "leaflet";
import { type ReactNode, useEffect } from "react";
import type { Coordinate } from "../../api/types";
import { usePrefersReducedMotion } from "../../hooks/usePrefersReducedMotion";

const MELBOURNE_CBD_CENTER: LatLngTuple = [-37.8136, 144.9631];

interface MapViewProps {
  children?: ReactNode;
  onMapClick?: (coordinate: Coordinate) => void;
  onCenterChange?: (coordinate: Coordinate) => void;
  panTarget?: Coordinate | null;
  panTargetKey?: string | number;
}

function ClickHandler({
  onMapClick,
  onCenterChange,
}: {
  onMapClick?: (coordinate: Coordinate) => void;
  onCenterChange?: (coordinate: Coordinate) => void;
}) {
  const map = useMapEvents({
    click(event) {
      onMapClick?.({ lat: event.latlng.lat, lng: event.latlng.lng });
    },
    moveend() {
      const center = map.getCenter();
      onCenterChange?.({ lat: center.lat, lng: center.lng });
    },
  });
  return null;
}

function ResizeHandler() {
  // Leaflet measures its container once at init and caches that size for
  // tile layout. If the flex layout around it (map + side panel) hasn't
  // settled yet — a near-guarantee on first paint — tiles clip at the stale
  // size even though the container div itself is the right width. A
  // ResizeObserver keeps Leaflet's cached size in sync with reality.
  const map = useMap();
  useEffect(() => {
    const container = map.getContainer();
    const observer = new ResizeObserver(() => map.invalidateSize());
    observer.observe(container);
    return () => observer.disconnect();
  }, [map]);
  return null;
}

function AccessibleContainer() {
  // MapContainer only accepts Leaflet options, not arbitrary DOM attributes
  // — an `aria-label` prop on it is silently dropped. Set it directly on the
  // underlying container div instead, so the map's accessible name doesn't
  // fall back to concatenating every descendant link's text (zoom buttons,
  // attribution links).
  const map = useMap();
  useEffect(() => {
    map.getContainer().setAttribute("aria-label", "Map of Melbourne CBD. Use arrow keys to pan, + and - to zoom.");
    map.getContainer().setAttribute("role", "application");
  }, [map]);
  return null;
}

function PanController({ target, targetKey }: { target?: Coordinate | null; targetKey?: string | number }) {
  const map = useMap();
  const prefersReducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    if (!target) return;
    if (prefersReducedMotion) {
      map.setView([target.lat, target.lng], map.getZoom());
    } else {
      map.panTo([target.lat, target.lng]);
    }
    // targetKey lets the caller force a re-pan to the same coordinate twice.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target?.lat, target?.lng, targetKey]);

  return null;
}

export function MapView({ children, onMapClick, onCenterChange, panTarget, panTargetKey }: MapViewProps) {
  return (
    <MapContainer
      center={MELBOURNE_CBD_CENTER}
      zoom={15}
      minZoom={13}
      maxZoom={18}
      style={{ height: "100%", width: "100%" }}
      keyboard
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <AccessibleContainer />
      <ResizeHandler />
      <ClickHandler onMapClick={onMapClick} onCenterChange={onCenterChange} />
      <PanController target={panTarget} targetKey={panTargetKey} />
      {children}
    </MapContainer>
  );
}

export { MELBOURNE_CBD_CENTER };
