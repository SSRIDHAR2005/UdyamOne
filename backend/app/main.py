from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import api_router
from app.database import engine, Base
import app.models.entities  # Ensure models are registered

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="UdyamOne - Airtel SYNC 2026 Enterprise Track A Digital Acquisition and Onboarding Platform"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "platform": "UdyamOne",
        "tagline": "One Conversation. One Smart Bundle. One Connected Business.",
        "hackathon": "Airtel SYNC 2026 / YTL Track A",
        "status": "RUNNING",
        "docs_url": "/docs"
    }

@app.get("/health")
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "UdyamOne API Gateway",
        "reference_date": settings.TODAY_DATE,
        "dpdp_version": settings.DPDP_CONSENT_VERSION,
        "catalogue_skus": 25,
        "environment": "demonstration_prototype"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

