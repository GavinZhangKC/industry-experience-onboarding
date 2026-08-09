import { Polyline } from "react-leaflet";
import type { RouteOption } from "../../api/types";
import { decodePolyline } from "../../utils/polyline";

const LEVEL_COLOR: Record<RouteOption["sensory"]["level"], string> = {
  low: "#3e7c59",
  medium: "#8a6d1b",
  high: "#9b3b3b",
};

// Line colour encodes sensory level, so two routes at the same level render
// in the same colour and can visually merge where their paths run close
// together. A dash pattern per rank keeps every route distinguishable on the
// map without relying on colour — the same "never colour alone" rule as the
// sensory badges, applied to route identity instead of sensory level.
const RANK_DASH: string[] = [undefined as unknown as string, "10 6", "2 8"];

interface RoutePolylinesProps {
  routes: RouteOption[];
  selectedRouteId: string | null;
  onSelectRoute: (routeId: string) => void;
}

export function RoutePolylines({ routes, selectedRouteId, onSelectRoute }: RoutePolylinesProps) {
  return (
    <>
      {routes.map((route, index) => {
        const isSelected = route.id === selectedRouteId;
        // No route selected yet: show all at full weight so the comparison
        // view reads clearly. Once one is selected, dim the rest — dimming
        // uses opacity and weight together, not colour alone.
        const dimmed = selectedRouteId !== null && !isSelected;
        return (
          <Polyline
            key={route.id}
            positions={decodePolyline(route.polyline)}
            pathOptions={{
              color: LEVEL_COLOR[route.sensory.level],
              weight: isSelected ? 6 : 4,
              opacity: dimmed ? 0.35 : 0.9,
              dashArray: RANK_DASH[index % RANK_DASH.length],
            }}
            eventHandlers={{
              click: () => onSelectRoute(route.id),
            }}
          />
        );
      })}
    </>
  );
}
