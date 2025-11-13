from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Request, status
from fastapi.responses import JSONResponse

import constants
from apps import UserModel
from core.data_encrypt.schemas import EncryptedRequest
from apps.user.schemas import BaseUserResponse
from apps.user.services import UserService
from core.auth import HasPermission
from core.types import RoleType
from core.utils.schema import BaseResponse
from core.utils.set_cookies import set_auth_cookies

router = APIRouter(prefix="/user", tags=["User"])


@router.post(
    "/sign-in",
    status_code=status.HTTP_200_OK,
    name="sign-in",
    description="sign-in",
    operation_id="sign_in",
)
async def sign_in(
    request: Request,
    body: Annotated[EncryptedRequest, Body()],
    service: Annotated[UserService, Depends()],
) -> JSONResponse:
    """
    Log in a user using email and password.

    Args:
        body (UserLoginRequest): The request object containing login information.
        service (AuthService): The authentication service.

    Returns:
        Response: The response with authentication cookies set.
    """

    res = await service.login_user(request=request, **body.model_dump())
    if "access_token" in res and res.get("access_token"):
        data = {"status": constants.SUCCESS,
                "code": status.HTTP_200_OK, "data": res}
        response = JSONResponse(content=data)
        return set_auth_cookies(response, res, RoleType.USER)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    name="Create user",
    description="Create user",
    operation_id="create_user",
)
async def create_user(
    request: Request,
    body: Annotated[EncryptedRequest, Body()],
    service: Annotated[UserService, Depends()],
) -> BaseResponse[BaseUserResponse]:
    """
    Create a new user.

    Args:
        body (CreateUserRequest): The request object containing user information.
        service (AuthService): The authentication service.

    Returns:
        BaseResponse[BaseUserResponse]: The response containing the created user information.
    """
    return BaseResponse(
        data=await service.create_user(request=request, **body.model_dump())
    )


@router.get(
    "/self",
    status_code=status.HTTP_200_OK,
    name="get self",
    description="Get Self",
    operation_id="get_self",
)
async def get_self_handler(
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[UserService, Depends()],
) -> BaseResponse[BaseUserResponse]:
    """
    Get data for a user.

    Args:
        user (UserModel): The authenticated user.
        service (AuthService): The authentication service.

    Returns:
        dict[str, Any]: The response containing the user data.
    """
    return BaseResponse(data=await service.get_self(user_id=user.id))


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(HasPermission(RoleType.USER))],
    name="get user by id",
    description="Get User By Id",
    operation_id="get_user_by_id",
)
async def get_user_by_id(
    user_id: Annotated[UUID, Path()], service: Annotated[UserService, Depends()]
) -> BaseResponse[BaseUserResponse]:
    """
    Get data for a user by ID.

    Args:
        user_id (int): The ID of the user.
        service (AuthService): The authentication service.

    Returns:
        dict[str, Any]: The response containing the user data.
    """
    return BaseResponse(data=await service.get_user_by_id(user_id=user_id))
