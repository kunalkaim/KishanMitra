from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    farmers,
    farms,
    soil,
    crops,
    recommendations,
    regions,
    weather,
    market,
    economics,
    advisory,
    assistant,
    documents,
    crop_rotation,
    feedback,
    analytics,
    notifications
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(farmers.router, prefix="/farmers", tags=["Farmers"])
api_router.include_router(farms.router, prefix="/farms", tags=["Farms"])
api_router.include_router(soil.router, prefix="/soil", tags=["Soil Health"])
api_router.include_router(crops.router, prefix="/crops", tags=["Crop Catalog"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Crop Recommendations"])
api_router.include_router(regions.router, prefix="/regions", tags=["Regional Intelligence"])
api_router.include_router(weather.router, prefix="/weather", tags=["Agro-Meteorology"])
api_router.include_router(market.router, prefix="/market", tags=["Market & Mandi Intelligence"])
api_router.include_router(economics.router, prefix="/economics", tags=["Cultivation Economics"])
api_router.include_router(advisory.router, prefix="/advisory", tags=["Pest & Disease Advisory (Text-Based)"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant (RAG)"])
api_router.include_router(documents.router, prefix="/documents", tags=["Knowledge Documents"])
api_router.include_router(crop_rotation.router, prefix="/crop-rotation", tags=["Crop Rotation Planning"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Farmer Feedback & Outcomes"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Decision Intelligence Analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications & Alerts"])
