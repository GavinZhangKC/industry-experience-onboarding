import type { RouteOption } from "../../api/types";
import { Button } from "../common/Button";
import { NoticeBanner } from "../common/NoticeBanner";
import { RouteCard } from "./RouteCard";
import styles from "./RouteComparisonPanel.module.css";

interface RouteComparisonPanelProps {
  routes: RouteOption[];
  selectedRouteId: string | null;
  onSelectRoute: (routeId: string) => void;
  onNewSearch: () => void;
  allRoutesExceedThreshold?: boolean;
}

// This list is the non-visual equivalent of the map: every route drawn on
// the map, its sensory level, and its explanation is also here as plain
// text, fully reachable and operable by keyboard.
export function RouteComparisonPanel({
  routes,
  selectedRouteId,
  onSelectRoute,
  onNewSearch,
  allRoutesExceedThreshold,
}: RouteComparisonPanelProps) {
  return (
    <section className={styles.panel} aria-labelledby="route-comparison-heading">
      <h2 id="route-comparison-heading" className={styles.title}>
        {routes.length} route{routes.length === 1 ? "" : "s"} found — calmest first
      </h2>
      {allRoutesExceedThreshold && (
        <NoticeBanner message="No route currently meets your comfort preference — showing the calmest option available." />
      )}
      <ul className={styles.list}>
        {routes.map((route) => (
          <RouteCard
            key={route.id}
            route={route}
            isSelected={route.id === selectedRouteId}
            onSelect={() => onSelectRoute(route.id)}
          />
        ))}
      </ul>
      <Button type="button" variant="secondary" onClick={onNewSearch}>
        New search
      </Button>
    </section>
  );
}
