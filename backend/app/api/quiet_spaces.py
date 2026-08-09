"""BE-F3 endpoint."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import settings_dep, store_dep
from app.config import Settings
from app.lib.data_store import DataStore
from app.schemas import QuietSpaceResponse, RefugeCategory
from app.services.refuge_service import find_quiet_spaces

router = APIRouter(prefix="/api/v1", tags=["quiet-spaces"])


@router.get("/quiet-spaces", response_model=QuietSpaceResponse)
def list_quiet_spaces(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    # None means "use settings.default_radius_m" — kept configurable there
    # rather than hard-coded here, alongside the other BE-F2 tunables.
    radius_m: int | None = Query(None, ge=100, le=5000),
    limit: int = Query(5, ge=1, le=20),
    category: RefugeCategory | None = Query(None, description="green_space | indoor, omitted means all"),
    store: DataStore = Depends(store_dep),
    settings: Settings = Depends(settings_dep),
) -> QuietSpaceResponse:
    effective_radius = radius_m if radius_m is not None else settings.default_radius_metres
    return find_quiet_spaces(
        lat,
        lng,
        radius_m=effective_radius,
        limit=limit,
        category=category,
        store=store,
        settings=settings,
    )
