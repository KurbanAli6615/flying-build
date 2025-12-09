from fastapi import APIRouter, Request
from starlette import status

from core.utils.schema import BaseResponse
from core.auth import HasPermission
from core.types import RoleType
from models import UserModel
from fastapi import Depends
from typing import Annotated
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
    return await service.create_team(request, user)
