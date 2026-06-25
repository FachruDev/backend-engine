from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.workspace.router import router as workspace_router


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


api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(workspace_router)

app.include_router(api_router, prefix=settings.app_api_prefix)
