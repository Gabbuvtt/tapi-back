"""
Main API router — aggregates all v1 module routers.
"""

from fastapi import APIRouter

from api.v1.auth.router import router as auth_router
from api.v1.businesses.router import router as businesses_router
from api.v1.reviews.router import router as reviews_router
from api.v1.loyalty.router import router as loyalty_router
from api.v1.nfc.router import router as nfc_router
from api.v1.metrics.router import router as metrics_router
from api.v1.menus.router import router as menus_router
from api.v1.notifications.router import router as notifications_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(businesses_router, prefix="/businesses", tags=["Businesses"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(loyalty_router, prefix="/loyalty", tags=["Loyalty"])
api_router.include_router(nfc_router, prefix="/nfc", tags=["NFC"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(menus_router, prefix="/menus", tags=["Menus"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
