from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, Params

import constants
from apps.admin.schemas import AdminListUsersResponse
from apps.admin.schemas.request import EncryptedRequest
from apps.admin.services import AdminUserService
from apps.user.models import UserModel
from apps.user.schemas import BaseUserResponse
from core.auth import AdminHasPermission
from core.types import RoleType
from core.utils.schema import BaseResponse
from core.utils.set_cookies import set_auth_cookies

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/sign-in",
    status_code=status.HTTP_200_OK,
    name="sign-in",
    description="sign-in",
    operation_id="sign_in_admin",
)
async def sign_in(
    request: Request,
    body: Annotated[EncryptedRequest, Body()],
    service: Annotated[AdminUserService, Depends()],
) -> JSONResponse:
    """
    Log in a user using email and password.

    Args:
        body (UserLoginRequest): The request object containing login information.
        service (AuthService): The authentication service.

    Returns:
        Response: The response with authentication cookies set.
    """

    res = await service.login_admin(request=request, **body.model_dump())
    if "access_token" in res and res.get("access_token"):
        data = {"status": constants.SUCCESS,
                "code": status.HTTP_200_OK, "data": res}
        response = JSONResponse(content=data)
        response = set_auth_cookies(response, res, RoleType.ADMIN)
        return response


@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AdminHasPermission())],
    name="Admin get all users",
    description="Admin get all users",
    operation_id="admin_get_users",
)
async def get_users(
    page_params: Annotated[Params, Depends()],
    service: Annotated[AdminUserService, Depends()],
) -> BaseResponse[Page[AdminListUsersResponse]]:
    """
    Get a paginated list of users.

    Args:
        page_params (Annotated[Params, Depends()]): Pagination parameters controlling the page size and number.
        service (AdminUserService): The service instance responsible for fetching users.

    Returns:
        BaseResponse[Page[AdminListUsersResponse]]:
            The response containing a paginated list of users.
            Each page of users is wrapped in an `AdminListUsersResponse`.
    """
    return BaseResponse(data=await service.get_users(params=page_params))


@router.get(
    "/self",
    status_code=status.HTTP_200_OK,
    name="get self",
    description="Get Self",
    operation_id="get_self_admin",
)
async def get_self_handler(
    user: Annotated[UserModel, Depends(AdminHasPermission())],
    service: Annotated[AdminUserService, Depends()],
) -> BaseResponse[BaseUserResponse]:
    """
    Get data for a user.

    Args:
        user (UserModel): The authenticated user.
        service (AuthService): The authentication service.

    Returns:
        dict[str, Any]: The response containing the user data.
    """
    return BaseResponse(data=await service.get_self_admin(user_id=user.id))


@router.patch(
    "/change-password",
    name="change password",
    description="Change Password",
    operation_id="change_password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: Request,
    user: Annotated[UserModel, Depends(AdminHasPermission())],
    body: Annotated[EncryptedRequest, Body()],
    service: Annotated[AdminUserService, Depends()],
) -> BaseResponse[BaseUserResponse]:
    """
    Change the password for a user.

    Args:
        user (UserModel): The authenticated user making the request.
        body (ChangePasswordRequest): The request containing the current and new passwords.
        service (AdminUserService): The service handling the password change logic.

    Returns:
        BaseResponse[BaseUserResponse]: The response containing the updated user data.
    """
    return BaseResponse(
        data=await service.change_password(
            request=request, **body.model_dump(), user=user.id
        )
    )
