from typing import Annotated

from fastapi import APIRouter, Depends, Request
from starlette import status

from core.auth import HasPermission
from core.types import RoleType
from core.utils.schema import BaseResponse
from models import UserModel

from ..services.team import TeamService

router = APIRouter(prefix="/team", tags=["Team"])


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    name="Create Team",
    description="Create Team",
    operation_id="create_team",
)
async def create_team(
    request: Request,
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse:
    """
    Create a new team for the authenticated user.
    
    Parameters:
        request (Request): FastAPI request containing the creation payload and request context.
        user (UserModel): Authenticated user with USER role performing the operation.
    
    Returns:
        BaseResponse: Response containing the created team's data and metadata.
    """
    return await service.create_team(request, user)