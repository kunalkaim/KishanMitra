from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import SessionLocal
from app.db.init_db import init_db
from scripts.seed_data import run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables and seed dataset
    db = SessionLocal()
    try:
        init_db(db)
        run_seed(db)
        # Pre-warm ML Predictor and RAG Retriever in memory to avoid request cold-start
        try:
            from app.ml.crop_recommendation.predictor import CropRecommendationPredictor
            CropRecommendationPredictor.get_instance()
            from app.api.v1.endpoints.recommendations import get_rag_retriever
            get_rag_retriever()
        except Exception as e:
            pass
    finally:
        db.close()
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend Decision Intelligence & Agronomic Platform for Indian Agriculture (Uttarakhand Pilot)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for container orchestrators and monitoring."""
    return {
        "status": "healthy",
        "service": "kisanmitra-backend",
        "version": settings.VERSION,
        "pilot_region": "Uttarakhand, India"
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to KisanMitra Decision Intelligence API",
        "tagline": "Know Your Land. Grow Smarter. Earn Better.",
        "docs": f"{settings.API_V1_STR}/docs"
    }
