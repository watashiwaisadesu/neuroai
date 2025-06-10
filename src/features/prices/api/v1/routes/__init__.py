from fastapi import APIRouter

from src.features.prices.api.v1.routes.create_price_router import create_price_router
from src.features.prices.api.v1.routes.get_prices_router import get_prices_router

price_router = APIRouter(prefix="/v1/prices", tags=["Prices"])

price_router.include_router(create_price_router)
price_router.include_router(get_prices_router)