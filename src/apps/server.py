from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

import constants
from apps.handlers import start_exception_handlers
from apps.user.controllers import user_router
from config import AppEnvironment, settings
from constants.config import rate_limiter_config
from core.data_encrypt.controller import data_decrypt_router
from core.task.lifespan import lifespan
from core.utils.schema import BaseValidationResponse


def init_routers(_app: FastAPI) -> None:
    """
    Initialize routers for the FastAPI application.

    Args:
        _app (FastAPI): The FastAPI application instance.
    """
    base_router = APIRouter(
        dependencies=[
            Depends(
                RateLimiter(
                    times=rate_limiter_config["request_limit"],
                    seconds=rate_limiter_config["time"],
                )
            )
        ]
    )
    base_router.include_router(data_decrypt_router)
    base_router.include_router(user_router)

    _app.include_router(base_router, responses={422: {"model": BaseValidationResponse}})


def root_health_path(_app: FastAPI) -> None:
    """
    Define root and health check endpoints for the FastAPI application.

    Args:
        _app (FastAPI): The FastAPI application instance.
    """

    @_app.get("/", include_in_schema=False)
    def root() -> JSONResponse:
        """
        Root endpoint.

        Returns:
            JSONResponse: A JSON response with a success message.
        """
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"message": constants.SUCCESS}
        )

    @_app.get("/healthcheck", include_in_schema=False)
    def healthcheck() -> JSONResponse:
        """
        Health check endpoint.

        Returns:
            JSONResponse: A JSON response with a success message.
        """
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"message": constants.SUCCESS}
        )


def init_middlewares(_app: FastAPI) -> None:
    """
    Initialize middlewares for the FastAPI application.

    Args:
        _app (FastAPI): The FastAPI application instance.
    """
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app(debug: bool = False) -> FastAPI:
    """
    Create and initialize the FastAPI application.

    Args:
        debug (bool, optional): Whether to enable debug mode. Defaults to False.

    Returns:
        FastAPI: The initialized FastAPI application instance.
    """
    _app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc" if debug else None,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "tryItOutEnabled": True,
            "requestSnippetsEnabled": True,
            "withCredentials": True,
            "persistAuthorization": True,
        },
        lifespan=lifespan,
    )
    init_routers(_app)
    root_health_path(_app)
    init_middlewares(_app)
    start_exception_handlers(_app)
    return _app


if settings.ENV != AppEnvironment.PRODUCTION:
    debug_app = create_app(debug=True)
else:
    production_app = create_app()
