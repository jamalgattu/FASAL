from fastapi import APIRouter

from app.api.v1 import auth, farmers, fpos, buyers, crops, produce, requirements, matches, orders, vehicles, deliveries

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(farmers.router)
api_router.include_router(fpos.router)
api_router.include_router(buyers.router)
api_router.include_router(crops.router)
api_router.include_router(produce.router)
api_router.include_router(requirements.router)
api_router.include_router(matches.router)
api_router.include_router(orders.router)
api_router.include_router(vehicles.router)
api_router.include_router(deliveries.router)
