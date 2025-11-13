import os
from enum import StrEnum
from typing import Optional

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

load_dotenv(override=True)


class AppEnvironment(StrEnum):
    """
    Enum representing different application environments.

    - LOCAL: Indicates that the application is running on a local machine or environment.
    - DEVELOPMENT: Indicates that the application is running in a development environment.
    - PRODUCTION: Indicates that the application is running in a production environment.
    """

    LOCAL = "Local"
    DEVELOPMENT = "Development"
    PRODUCTION = "Production"


class Settings(BaseSettings):
    """
    A settings class for the project defining all the necessary parameters within the
    app through an object.
    """

    # App variables
    ENV: AppEnvironment = os.getenv("ENV")  # type: ignore
    APP_NAME: str | None = os.getenv("APP_NAME")
    APP_VERSION: str | None = os.getenv("APP_VERSION")
    APP_HOST: str | None = os.getenv("APP_HOST")
    APP_PORT: Optional[int] = os.getenv("APP_PORT")  # type: ignore
    APP_DEBUG: Optional[bool] = os.getenv("APP_DEBUG")  # type: ignore
    APP_CONTAINER: Optional[bool] = os.getenv("APP_CONTAINER")  # type: ignore

    # JWT Token variables
    JWT_SECRET_KEY: str | None = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str | None = os.getenv("JWT_ALGORITHM")
    COOKIES_DOMAIN: Optional[str] = os.getenv("COOKIES_DOMAIN")
    ACCESS_TOKEN_EXP: Optional[int] = os.getenv("ACCESS_TOKEN_EXP")  # type: ignore
    REFRESH_TOKEN_EXP: Optional[int] = os.getenv("REFRESH_TOKEN_EXP")  # type: ignore

    DATABASE_USER: str | None = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: str | None = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST: str | None = os.getenv("DATABASE_HOST")
    DATABASE_PORT: str | None = os.getenv("DATABASE_PORT")
    DATABASE_NAME: str | None = os.getenv("DATABASE_NAME")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    REDIS_URL: str | None = os.getenv("REDIS_URL")

    PRIVATE_PUBLIC_KEY_PATH: str | None = os.getenv("PRIVATE_PUBLIC_KEY_PATH")
    PUBLIC_KEY_PATH: str | None = os.getenv("PUBLIC_KEY_PATH")


    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_url(cls, val, values) -> str:
        """
        Create a Database URL from the settings provided in the .env file.
        """
        if isinstance(val, str):
            return val

        database_user = values.data.get("DATABASE_USER")
        database_password = values.data.get("DATABASE_PASSWORD")
        database_host = values.data.get("DATABASE_HOST")
        database_port = values.data.get("DATABASE_PORT").replace('"', "")
        database_name = values.data.get("DATABASE_NAME")

        if not all(
            [
                database_user,
                database_password,
                database_host,
                database_port,
                database_name,
            ]
        ):
            raise ValueError("Incomplete database connection information")

        return (
            f"postgresql+asyncpg://"
            f"{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"
        )

    @property
    def is_production(self) -> bool:
        """
        Check if the app is running in production mode.
        """
        return self.ENV == AppEnvironment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """
        Check if the app is running in development mode.
        """
        return self.ENV == AppEnvironment.DEVELOPMENT

    @property
    def is_local(self) -> bool:
        """
        Check if the app is running in local mode.
        """
        return self.ENV == AppEnvironment.LOCAL


settings = Settings()
