from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.config import settings
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Backend for the Fasal farmer-buyer-logistics coordination platform "
        "(SIH problem 26033). Frontend-only prototype now wired to a real "
        "API — matching and route optimization use configurable rule-based "
        "engines, not ML/AI in this phase."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
