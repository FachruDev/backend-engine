from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "version": "0.1.0",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


api_router = APIRouter()


@api_router.get("/health")
def api_health_check() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(api_router, prefix=settings.app_api_prefix)
