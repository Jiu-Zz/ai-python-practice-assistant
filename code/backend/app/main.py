from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, session_scope
from app.core.errors import AppError
from app.core.responses import error_response
from app.data.seed import seed_initial_data
from app.routers import ai, auth, problems, recommendations, users


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()
        with session_scope() as db:
            seed_initial_data(db)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content=error_response(exc.message))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        if settings.debug:
            message = f"{exc.__class__.__name__}: {exc}"
        else:
            message = "服务器内部错误"
        return JSONResponse(status_code=500, content=error_response(message))

    @app.get("/health")
    def health():
        return {"status": "ok", "app": settings.app_name}

    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(problems.router, prefix=api_prefix)
    app.include_router(ai.router, prefix=api_prefix)
    app.include_router(recommendations.router, prefix=api_prefix)
    return app


app = create_app()
