import json

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import constants
from core.exceptions import CustomException, UnexpectedResponse


def start_exception_handlers(_app: FastAPI) -> None:
    """
    Define exception handlers for the FastAPI application.

    Args:
        _app (FastAPI): The FastAPI application instance.
    """

    @_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(*args) -> JSONResponse:
        """
        Handle RequestValidationError within the application.
         Args:
            *args: Variable length arguments passed to the handler.

        Returns:
            JSONResponse: JSON response containing the validation error details
        """
        exc = args[1]
        transformed_errors = [
            {
                (
                    error["loc"][1]
                    if "loc" in error and len(error["loc"]) > 1
                    else "message"
                ): error["msg"]
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": constants.ERROR,
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": transformed_errors,
            },
        )

    @_app.exception_handler(CustomException)
    async def custom_exception_handler(*args) -> JSONResponse:
        """
        Handle CustomException within the application.
         Args:
            *args: Variable length arguments passed to the handler.

        Returns:
            JSONResponse: JSON response containing the validation error details
        """
        exc = args[1]
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": constants.ERROR,
                "code": exc.status_code,
                "message": exc.message,
            },
        )

    @_app.exception_handler(UnexpectedResponse)
    async def unexpected_response(_request: Request, exc: UnexpectedResponse):
        """
        Handler for UnexpectedResponse raised within the application.

        Args:
            _request (Request): The request object.
            exc (UnexpectedResponse): The exception instance.

        Returns:
            JSONResponse: The JSON response containing the unexpected response details.
        """
        return JSONResponse(
            status_code=exc.response.status_code,
            content={
                "status": constants.ERROR,
                "code": exc.response.status_code,
                "message": json.loads(exc.response.content),
            },
        )
