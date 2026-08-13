import { useEffect, useState } from "react";
import type { Coordinate, QuietSpace } from "./api/types";
import { MELBOURNE_LANDMARKS } from "./constants/landmarks";
import { AppShell } from "./components/layout/AppShell";
import { LandingPage } from "./components/landing/LandingPage";
import { MapView } from "./components/map/MapView";
import { OriginDestinationMarkers } from "./components/map/OriginDestinationMarkers";
import { RoutePolylines } from "./components/map/RoutePolylines";
import { QuietSpaceMarkers } from "./components/map/QuietSpaceMarkers";
import { JourneyInputPanel, type PickingField } from "./components/journey/JourneyInputPanel";
import { RouteComparisonPanel } from "./components/routes/RouteComparisonPanel";
import { FindQuietSpaceButton } from "./components/quietSpaces/FindQuietSpaceButton";
import { QuietSpaceResultsPanel } from "./components/quietSpaces/QuietSpaceResultsPanel";
import { useRoutes } from "./hooks/useRoutes";
import { useQuietSpaces, RADIUS_STEPS_M } from "./hooks/useQuietSpaces";
import { SelectedRouteSummary } from "./components/routes/SelectedRouteSummary";
import {
  isWithinQuietSpaceServiceArea,
  QUIET_SPACE_CBD_CENTER,
} from "./lib/quietSpaceServiceArea";

type PrimaryView = "input" | "routes";

interface PlannerAppProps {
  onBackToLanding: () => void;
}

function PlannerApp({
  onBackToLanding,
}: PlannerAppProps) {
  const [origin, setOrigin] = useState<Coordinate | null>(null);
  const [destination, setDestination] = useState<Coordinate | null>(null);
  const [originLandmarkId, setOriginLandmarkId] = useState<string | null>(null);
  const [destinationLandmarkId, setDestinationLandmarkId] = useState<string | null>(null);
  const [pickingField, setPickingField] = useState<PickingField>(null);

  const [primaryView, setPrimaryView] = useState<PrimaryView>("input");
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);

  const [panTarget, setPanTarget] = useState<Coordinate | null>(null);
  const [panTargetKey, setPanTargetKey] = useState(0);

  const [quietSpacePanelOpen, setQuietSpacePanelOpen] = useState(false);
  const [selectedQuietSpaceId, setSelectedQuietSpaceId] = useState<string | null>(null);
  const [quietSpaceLocationNote, setQuietSpaceLocationNote] = useState<string | null>(null);
  const [pickingQuietSpaceLocation, setPickingQuietSpaceLocation] = useState(false);
  const [quietSpaceCenterLabel, setQuietSpaceCenterLabel] = useState("Search location");

  const routes = useRoutes();
  const quietSpaces = useQuietSpaces();

  // Switches to the comparison view only once a search actually succeeds,
  // instead of racing the async call in the click handler.
  useEffect(() => {
    if (routes.routes) {
      setPrimaryView("routes");
      setSelectedRouteId(null);
    }
  }, [routes.routes]);

  function panTo(coordinate: Coordinate) {
    setPanTarget(coordinate);
    setPanTargetKey((key) => key + 1);
  }

  function handleSelectLandmark(field: "origin" | "destination", landmarkId: string) {
    if (landmarkId === "") {
      handleClearField(field);
      return;
    }
    const landmark = MELBOURNE_LANDMARKS.find((entry) => entry.id === landmarkId);
    if (!landmark) return;
    if (field === "origin") {
      setOrigin(landmark.coordinate);
      setOriginLandmarkId(landmarkId);
    } else {
      setDestination(landmark.coordinate);
      setDestinationLandmarkId(landmarkId);
    }
    setPickingField(null);
    panTo(landmark.coordinate);
  }

  function handleTogglePicking(field: "origin" | "destination") {
    setPickingField((current) => (current === field ? null : field));
  }

  function handleClearField(field: "origin" | "destination") {
    if (field === "origin") {
      setOrigin(null);
      setOriginLandmarkId(null);
    } else {
      setDestination(null);
      setDestinationLandmarkId(null);
    }
    setPickingField((current) => (current === field ? null : current));
  }

  function handleClearAll() {
    setOrigin(null);
    setDestination(null);
    setOriginLandmarkId(null);
    setDestinationLandmarkId(null);
    setPickingField(null);
    routes.reset();
    setSelectedRouteId(null);
    setPrimaryView("input");
  }

  function handleMapClick(coordinate: Coordinate) {
    if (pickingQuietSpaceLocation) {
      if (!isWithinQuietSpaceServiceArea(coordinate)) {
        setQuietSpaceLocationNote(
          "That point is outside the Melbourne CBD search area. Please choose a point closer to the CBD.",
        );
        return;
      }
      setPickingQuietSpaceLocation(false);
      setQuietSpaceLocationNote("Searching near the point you selected on the map.");
      setQuietSpaceCenterLabel("Selected search location");
      setSelectedQuietSpaceId(null);
      panTo(coordinate);
      quietSpaces.search(coordinate);
      return;
    }
    if (pickingField === "origin") {
      setOrigin(coordinate);
      setOriginLandmarkId(null);
      setPickingField(null);
    } else if (pickingField === "destination") {
      setDestination(coordinate);
      setDestinationLandmarkId(null);
      setPickingField(null);
    }
  }

  function handleSearchRoutes() {
    if (!origin || !destination) return;
    routes.search(origin, destination);
  }

  function handleNewSearch() {
    setPrimaryView("input");
    routes.reset();
    setSelectedRouteId(null);
  }

  function handleFindQuietSpace(center: Coordinate, note: string | null) {
    setQuietSpacePanelOpen(true);
    setPickingQuietSpaceLocation(false);
    setPickingField(null);
    setSelectedQuietSpaceId(null);
    setQuietSpaceLocationNote(note);
    setQuietSpaceCenterLabel("Your location");
    panTo(center);
    quietSpaces.search(center);
  }

  function handlePickQuietSpaceOnMap(message: string) {
    setQuietSpacePanelOpen(true);
    setPickingQuietSpaceLocation(true);
    setPickingField(null);
    setSelectedQuietSpaceId(null);
    setQuietSpaceLocationNote(message);
    setQuietSpaceCenterLabel("Selected search location");
    quietSpaces.reset();
    panTo(QUIET_SPACE_CBD_CENTER);
  }

  function handleSelectQuietSpace(space: QuietSpace) {
    setSelectedQuietSpaceId(space.id);
    panTo({ lat: space.lat, lng: space.lng });
  }

  function handleCloseQuietSpacePanel() {
    setQuietSpacePanelOpen(false);
    setPickingQuietSpaceLocation(false);
    setSelectedQuietSpaceId(null);
    setQuietSpaceLocationNote(null);
    quietSpaces.reset();
  }

  const nextRadiusIndex = quietSpaces.data
    ? RADIUS_STEPS_M.indexOf(quietSpaces.data.radius_m as (typeof RADIUS_STEPS_M)[number])
    : -1;
  const nextRadiusM = nextRadiusIndex >= 0 ? (RADIUS_STEPS_M[nextRadiusIndex + 1] ?? null) : null;

  const sidePanel = quietSpacePanelOpen ? (
    <QuietSpaceResultsPanel
      data={quietSpaces.data}
      loading={quietSpaces.loading}
      error={quietSpaces.error}
      locationNote={quietSpaceLocationNote}
      selectedSpaceId={selectedQuietSpaceId}
      category={quietSpaces.category}
      onCategoryChange={
        quietSpaces.changeCategory
      }
      onSelectSpace={
        handleSelectQuietSpace
      }
      onBackFromDetail={() =>
        setSelectedQuietSpaceId(null)
      }
      onClose={
        handleCloseQuietSpacePanel
      }
      canExpand={
        quietSpaces.canExpand
      }
      nextRadiusM={nextRadiusM}
      onExpandRadius={
        quietSpaces.expandRadius
      }
    />
  ) : primaryView === "routes" && routes.routes ? (
    <RouteComparisonPanel
      routes={routes.routes}
      selectedRouteId={selectedRouteId}
      onSelectRoute={setSelectedRouteId}
      onNewSearch={handleNewSearch}
    />
  ) : (
    <>
      <JourneyInputPanel
        origin={origin}
        destination={destination}
        originLandmarkId={originLandmarkId}
        destinationLandmarkId={destinationLandmarkId}
        pickingField={pickingField}
        onSelectLandmark={handleSelectLandmark}
        onTogglePicking={handleTogglePicking}
        onClearField={handleClearField}
        onClearAll={handleClearAll}
        onSearch={handleSearchRoutes}
        quietSpaceAction={
          <FindQuietSpaceButton
            onFind={handleFindQuietSpace}
            onPickOnMap={handlePickQuietSpaceOnMap}
          />
        }
        loading={routes.loading}
        error={routes.error}
      />
    </>
  );

  const selectedRoute =
  routes.routes?.find(
    (route) => route.id === selectedRouteId
  ) ?? null;

  return (
      <AppShell
        onBackToLanding={onBackToLanding}
        map={
        <MapView onMapClick={handleMapClick} panTarget={panTarget} panTargetKey={panTargetKey}>
          <OriginDestinationMarkers origin={origin} destination={destination} />
          {primaryView === "routes" && routes.routes && (
            <RoutePolylines routes={routes.routes} selectedRouteId={selectedRouteId} onSelectRoute={setSelectedRouteId} />
          )}
          {quietSpacePanelOpen && quietSpaces.center && (
            <QuietSpaceMarkers
              spaces={quietSpaces.data?.quiet_spaces ?? []}
              selectedId={selectedQuietSpaceId}
              onSelect={handleSelectQuietSpace}
              searchCenter={quietSpaces.center}
              radiusM={quietSpaces.data?.radius_m ?? RADIUS_STEPS_M[0]}
              searchCenterLabel={quietSpaceCenterLabel}
            />
          )}
        </MapView>
      }
      mapOverlay={
        selectedRoute ? (
          <SelectedRouteSummary
            route={selectedRoute}
            onExit={() => setSelectedRouteId(null)}
          />
        ) : null
      }
      sidePanel={sidePanel}
    />
  );
}

function App() {
  const [hasEntered, setHasEntered] = useState(false);

  if (!hasEntered) {
    return (
      <LandingPage
        onEnter={() => setHasEntered(true)}
      />
    );
  }

  return (
    <PlannerApp
      onBackToLanding={() => setHasEntered(false)}
    />
  );
}

export default App;
