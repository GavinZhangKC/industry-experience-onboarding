"""BE-F1 + BE-F2 endpoint. Thin: validate, delegate, return."""

from fastapi import APIRouter, Depends

from app.api.deps import maps_dep, settings_dep, store_dep
from app.clients.maps_client import MapsClient
from app.config import Settings
from app.lib.data_store import DataStore
from app.schemas import RouteRequest, RouteResponse
from app.services.route_service import plan_routes

router = APIRouter(prefix="/api/v1", tags=["routes"])


@router.post("/routes", response_model=RouteResponse)
async def create_routes(
    request: RouteRequest,
    maps_client: MapsClient = Depends(maps_dep),
    store: DataStore = Depends(store_dep),
    settings: Settings = Depends(settings_dep),
) -> RouteResponse:
    return await plan_routes(
        request, maps_client=maps_client, store=store, settings=settings
    )
