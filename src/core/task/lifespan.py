from contextlib import asynccontextmanager

from cryptography.hazmat.primitives import serialization
from fastapi_limiter import FastAPILimiter

from config import settings
from core.db import redis
from core.utils import logger, scheduler


@asynccontextmanager
async def lifespan(app):
    """Asynchronous context manager to manage the lifespan of the application.

    This function reads a private RSA key from a specified file and stores
    it in the application state for later use. It ensures that the RSA key
    is properly loaded into the application state before yielding control to
    the application and does not perform any cleanup actions upon exit.

    Args:
        app: The application instance, which can be used to store
             application-level state and configurations.

    Yields:
        None: Control is yielded back to the application, allowing it to
              run while the RSA key is available in the app state.
    """
    logger.info("Application started.....")
    # Load the RSA private key using cryptography
    with open(settings.PRIVATE_PUBLIC_KEY_PATH, "rb") as private_key_file:
        private_key_data = private_key_file.read()
    app.state.rsa_key = serialization.load_pem_private_key(
        private_key_data,
        password=None  # Set password if your key is encrypted
    )

    logger.info("starting scheduler")

    scheduler.start()
    await FastAPILimiter.init(redis)
    yield
    