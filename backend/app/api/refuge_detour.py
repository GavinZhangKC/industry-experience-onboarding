"""BE-F3 extension (AC5): detour to a refuge and back onto the original route."""

from fastapi import APIRouter, Depends

from app.api.deps import maps_dep, settings_dep, store_dep
from app.clients.maps_client import MapsClient
from app.config import Settings
from app.lib.data_store import DataStore
from app.schemas import RefugeDetourRequest, RefugeDetourResponse
from app.services.refuge_service import plan_refuge_detour

router = APIRouter(prefix="/api/v1", tags=["refuge-detour"])


@router.post("/refuge-detour", response_model=RefugeDetourResponse)
async def create_refuge_detour(
    request: RefugeDetourRequest,
    maps_client: MapsClient = Depends(maps_dep),
    store: DataStore = Depends(store_dep),
    settings: Settings = Depends(settings_dep),
) -> RefugeDetourResponse:
    return await plan_refuge_detour(
        request, maps_client=maps_client, store=store, settings=settings
    )
