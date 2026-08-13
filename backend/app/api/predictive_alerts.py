"""US 2.2 endpoint."""

from fastapi import APIRouter, Depends

from app.api.deps import store_dep
from app.lib.data_store import ReferenceDataStore
from app.schemas import PredictiveAlertsResponse
from app.services.predictive_alerts_service import get_predictive_alerts

router = APIRouter(prefix="/api/v1", tags=["predictive-alerts"])


@router.get("/predictive-alerts", response_model=PredictiveAlertsResponse)
def list_predictive_alerts(
    store: ReferenceDataStore = Depends(store_dep),
) -> PredictiveAlertsResponse:
    return get_predictive_alerts(store=store)
