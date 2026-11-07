import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseModel):
    APP_NAME: str = "UdyamOne - Airtel SYNC 2026"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/udyamone.db")
    DATA_DIR: Path = DATA_DIR
    TODAY_DATE: str = "2026-07-15"  # Fixed reference date from YTL Hackathon Track A README
    DPDP_CONSENT_VERSION: str = "DPDP-2026-V1.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "udyamone-secret-key-airtel-sync-2026-b2b")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)

settings = Settings()

