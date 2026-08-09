"""Shared FastAPI dependencies. The only file that couples HTTP to services."""

from fastapi import Depends

from app.clients.maps_client import MapsClient, get_maps_client
from app.config import Settings, get_settings
from app.lib.data_store import ReferenceDataStore, get_configured_data_store


def settings_dep() -> Settings:
    return get_settings()


def store_dep(settings: Settings = Depends(settings_dep)) -> ReferenceDataStore:
    return get_configured_data_store(settings)


def maps_dep(settings: Settings = Depends(settings_dep)) -> MapsClient:
    return get_maps_client(settings)
