from fastapi import APIRouter, Depends

from app.api.deps import settings_dep, store_dep
from app.config import Settings
from app.lib.data_store import DataStore

router = APIRouter(tags=["meta"])


@router.get("/health")
def health(
    settings: Settings = Depends(settings_dep),
    store: DataStore = Depends(store_dep),
):
    """Liveness plus a quick view of what data is loaded.

    Note it reports the provider name only — never the key.
    """
    return {
        "status": "ok",
        "maps_provider": settings.maps_provider,
        "busy_areas": len(store.busy_areas),
        "quiet_spaces": len(store.quiet_spaces),
    }
