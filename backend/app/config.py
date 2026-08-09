"""Application settings.

BE-F5: every secret and every tunable lives in the environment, never in code.
Copy .env.example to .env and fill it in. .env is gitignored.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Mapping provider -------------------------------------------------
    # "mock" generates synthetic routes so the whole team can develop without
    # a Google key or a billing account. Switch to "google" when the key exists.
    maps_provider: str = Field("mock", description="mock | google")
    google_maps_api_key: str = ""

    # --- CORS (BE-F5) -----------------------------------------------------
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # --- Rate limiting (BE-F5) -------------------------------------------
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # --- Refuge search (BE-F3) --------------------------------------------
    # AC criterion: at least 3 refuges within an 800 m walking radius.
    default_radius_metres: int = 800

    # --- Service area guard ----------------------------------------------
    # Deliberately generous: covers greater Melbourne, not just the CBD, so
    # the Abbotsford coordinates in the prototype mockups still validate.
    min_lat: float = -38.10
    max_lat: float = -37.55
    min_lng: float = 144.55
    max_lng: float = 145.35

    # --- Sensory scoring (BE-F2) -----------------------------------------
    proximity_metres: float = 120.0
    low_threshold: int = 33
    medium_threshold: int = 66

    # --- Misc -------------------------------------------------------------
    request_timeout_seconds: float = 8.0
    log_level: str = "INFO"
    data_dir: str = "data"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
