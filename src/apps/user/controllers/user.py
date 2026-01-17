from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.responses import JSONResponse

import constants
from apps.user.schemas import BaseUserResponse, PublicKeyResponse
from apps.user.services import UserService
from core.auth import HasPermission
from core.data_encrypt.schemas import EncryptedRequest
from core.types import RoleType
from core.utils.schema import BaseResponse, SuccessResponse
from core.utils.set_cookies import set_auth_cookies
from models import UserModel

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
    Authenticate a user with submitted credentials and return a JSON response containing authentication data.

    Parameters:
        body (EncryptedRequest): Encrypted wrapper of the login payload (contains email and password).

    Returns:
        JSONResponse: Response with keys `"status"`, `"code"`, and `"data"` (authentication payload). The response includes authentication cookies set for the USER role.
    """

    res = await service.login_user(request=request, **body.model_dump())
    data = {
        "status": constants.SUCCESS,
        "code": status.HTTP_200_OK,
        "data": res.model_dump(),
    }
    response = JSONResponse(content=data)
    set_auth_cookies(response, res, RoleType.USER)
    return response


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
) -> BaseResponse[SuccessResponse]:
    """
    Create a new user account from an encrypted request.

    Parameters:
        body (EncryptedRequest): Encrypted request containing the fields required to create a user (equivalent to a `CreateUserRequest` payload).

    Returns:
        BaseResponse[SuccessResponse]: The service's success result wrapped in a BaseResponse.
    """
    response = await service.create_user(request=request, **body.model_dump())
    return BaseResponse(data=response)


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
    "/public-key",
    status_code=status.HTTP_200_OK,
    name="get public key",
    description="Get Public Key",
    operation_id="get_public_key",
)
async def get_public_key(
    service: Annotated[UserService, Depends()]
) -> BaseResponse[PublicKeyResponse]:
    """
    Get the RSA public key for encryption.

    This endpoint returns the public key that clients can use to encrypt
    data before sending it to the API.

    Returns:
        BaseResponse[PublicKeyResponse]: The response containing the public key in PEM format.
    """
    return BaseResponse(data=await service.get_public_key())
