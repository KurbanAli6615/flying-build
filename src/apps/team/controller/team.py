from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Request, status

from apps.team.schemas.request import (
    CreateTeamRequest,
    JoinTeamRequest,
    PromoteToAdminRequest,
    ToggleTeamActiveRequest,
    UpdateTeamRequest,
)
from apps.team.schemas.response import (
    JoinRequestListResponse,
    JoinRequestResponse,
    TeamListResponse,
    TeamMemberListResponse,
    TeamResponse,
)
from apps.team.services.team import TeamService
from core.auth import HasPermission, HasTeamPermission
from core.types import RoleType, TeamRole
from core.utils.schema import BaseResponse, SuccessResponse
from models import TeamMemberModel, UserModel

router = APIRouter(prefix="/team", tags=["Team"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    name="create team",
    description="Create Team",
    operation_id="create_team",
)
async def create_team(
    request: Request,
    body: Annotated[CreateTeamRequest, Body()],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[TeamResponse]:
    """
    Create a new team.

    Args:
        request: FastAPI request object.
        body: Team creation data.
        user: Authenticated user.
        service: Team service.

    Returns:
        BaseResponse[TeamResponse]: Created team data.
    """
    return BaseResponse(data=await service.create_team(request, user, body))


@router.get(
    "/my",
    status_code=status.HTTP_200_OK,
    name="list my teams",
    description="List My Teams",
    operation_id="list_my_teams",
)
async def list_my_teams(
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[TeamListResponse]:
    """
    List all teams where the user is a member.

    Args:
        user: Authenticated user.
        service: Team service.

    Returns:
        BaseResponse[TeamListResponse]: List of teams.
    """
    teams = await service.list_my_teams(user)
    return BaseResponse(data=TeamListResponse(teams=teams))


@router.get(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
    name="get team",
    description="Get Team",
    operation_id="get_team",
)
async def get_team(
    team_id: Annotated[UUID, Path()],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[TeamResponse]:
    """
    Get team details by ID.

    Args:
        team_id: The team's unique identifier.
        user: Authenticated user.
        service: Team service.

    Returns:
        BaseResponse[TeamResponse]: Team data.
    """
    return BaseResponse(data=await service.get_team_by_id(team_id, user))


@router.patch(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
    name="update team",
    description="Update Team",
    operation_id="update_team",
)
async def update_team(
    team_id: Annotated[UUID, Path()],
    body: Annotated[UpdateTeamRequest, Body()],
    team_member: Annotated[
        TeamMemberModel, Depends(HasTeamPermission([TeamRole.OWNER, TeamRole.ADMIN]))
    ],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[TeamResponse]:
    """
    Update team name or description.

    Args:
        team_id: The team's unique identifier.
        body: Update data.
        team_member: Team membership info (from HasTeamPermission).
        user: Authenticated user.
        service: Team service.

    Returns:
        BaseResponse[TeamResponse]: Updated team data.
    """
    return BaseResponse(data=await service.update_team(team_id, user, body))


@router.patch(
    "/{team_id}/active",
    status_code=status.HTTP_200_OK,
    name="toggle team active status",
    description="Toggle Team Active Status",
    operation_id="toggle_team_active_status",
)
async def toggle_team_active_status(
    team_id: Annotated[UUID, Path()],
    body: Annotated[ToggleTeamActiveRequest, Body()],
    team_member: Annotated[
        TeamMemberModel, Depends(HasTeamPermission([TeamRole.OWNER]))
    ],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[SuccessResponse]:
    """
    Toggle team active/deactive status.

    Only the team owner can activate or deactivate the team.

    Args:
        team_id: The team's unique identifier.
        body: Toggle data with is_active flag.
        team_member: Team membership info (from HasTeamPermission).
        user: Authenticated user (team owner).
        service: Team service.

    Returns:
        BaseResponse[SuccessResponse]: Success message.
    """
    return BaseResponse(
        data=await service.toggle_team_active_status(team_id, user, body)
    )


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
    name="delete team",
    description="Delete Team",
    operation_id="delete_team",
)
async def delete_team(
    team_id: Annotated[UUID, Path()],
    team_member: Annotated[
        TeamMemberModel, Depends(HasTeamPermission([TeamRole.OWNER]))
    ],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[SuccessResponse]:
    """
    Delete a team (soft delete).

    Only the team owner can delete the team. This sets is_active=False.

    Args:
        team_id: The team's unique identifier.
        team_member: Team membership info (from HasTeamPermission).
        user: Authenticated user (team owner).
        service: Team service.

    Returns:
        BaseResponse[SuccessResponse]: Success message.
    """
    return BaseResponse(data=await service.delete_team(team_id, user))


@router.get(
    "/{team_id}/members",
    status_code=status.HTTP_200_OK,
    name="list team members",
    description="List Team Members",
    operation_id="list_team_members",
)
async def list_team_members(
    team_id: Annotated[UUID, Path()],
    team_member: Annotated[TeamMemberModel, Depends(HasTeamPermission())],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[TeamMemberListResponse]:
    """
    List all team members with their roles.

    All team members (OWNER, ADMIN, MEMBER) can view the team members list.

    Args:
        team_id: The team's unique identifier.
        team_member: Team membership info (from HasTeamPermission).
        user: Authenticated user.
        service: Team service.

    Returns:
        BaseResponse[TeamMemberListResponse]: List of team members.
    """
    members = await service.list_team_members(team_id, user)
    return BaseResponse(data=TeamMemberListResponse(members=members))


@router.post(
    "/{team_id}/admin",
    status_code=status.HTTP_200_OK,
    name="promote to admin",
    description="Promote To Admin",
    operation_id="promote_to_admin",
)
async def promote_to_admin(
    team_id: Annotated[UUID, Path()],
    body: Annotated[PromoteToAdminRequest, Body()],
    team_member: Annotated[
        TeamMemberModel, Depends(HasTeamPermission([TeamRole.OWNER]))
    ],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[SuccessResponse]:
    """
    Promote a user to admin role.

    Args:
        team_id: The team's unique identifier.
        body: Promotion data with user_id.
        team_member: Team membership info (from HasTeamPermission).
        user: Authenticated user (team owner).
        service: Team service.

    Returns:
        BaseResponse[SuccessResponse]: Success message.
    """
    return BaseResponse(data=await service.promote_to_admin(team_id, body, user))


@router.delete(
    "/{team_id}/admin/{user_id}",
    status_code=status.HTTP_200_OK,
    name="demote from admin",
    description="Demote From Admin",
    operation_id="demote_from_admin",
)
async def demote_from_admin(
    team_id: Annotated[UUID, Path()],
    user_id: Annotated[UUID, Path()],
    team_member: Annotated[
        TeamMemberModel, Depends(HasTeamPermission([TeamRole.OWNER]))
    ],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[SuccessResponse]:
    """
    Demote an admin to member role.

    Args:
        team_id: The team's unique identifier.
        user_id: The user to demote.
        team_member: Team membership info (from HasTeamPermission).
        user: Authenticated user (team owner).
        service: Team service.

    Returns:
        BaseResponse[SuccessResponse]: Success message.
    """
    return BaseResponse(data=await service.demote_from_admin(team_id, user_id, user))


@router.post(
    "/join/request",
    status_code=status.HTTP_201_CREATED,
    name="create join request",
    description="Create Join Request",
    operation_id="create_join_request",
)
async def create_join_request(
    body: Annotated[JoinTeamRequest, Body()],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[JoinRequestResponse]:
    """
    Create a join request using team code.

    Args:
        body: Join request data with team_code.
        user: Authenticated user.
        service: Team service.

    Returns:
        BaseResponse[JoinRequestResponse]: Created join request data.
    """
    return BaseResponse(data=await service.create_join_request(body, user))


@router.get(
    "/{team_id}/join-requests",
    status_code=status.HTTP_200_OK,
    name="list team join requests",
    description="List Team Join Requests",
    operation_id="list_team_join_requests",
)
async def list_team_join_requests(
    team_id: Annotated[UUID, Path()],
    team_member: Annotated[
        TeamMemberModel, Depends(HasTeamPermission([TeamRole.OWNER]))
    ],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[JoinRequestListResponse]:
    """
    List all join requests for a team.

    Args:
        team_id: The team's unique identifier.
        team_member: Team membership info (from HasTeamPermission).
        user: Authenticated user (team owner).
        service: Team service.

    Returns:
        BaseResponse[JoinRequestListResponse]: List of join requests.
    """
    join_requests = await service.list_team_join_requests(team_id, user)
    return BaseResponse(data=JoinRequestListResponse(join_requests=join_requests))


@router.post(
    "/join-request/{request_id}/approve",
    status_code=status.HTTP_200_OK,
    name="approve join request",
    description="Approve Join Request",
    operation_id="approve_join_request",
)
async def approve_join_request(
    request_id: Annotated[UUID, Path()],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[JoinRequestResponse]:
    """
    Approve a join request and add user as team member.

    Args:
        request_id: The join request's unique identifier.
        user: Authenticated user (team owner).
        service: Team service.

    Returns:
        BaseResponse[JoinRequestResponse]: Updated join request data.
    """
    return BaseResponse(data=await service.approve_join_request(request_id, user))


@router.post(
    "/join-request/{request_id}/reject",
    status_code=status.HTTP_200_OK,
    name="reject join request",
    description="Reject Join Request",
    operation_id="reject_join_request",
)
async def reject_join_request(
    request_id: Annotated[UUID, Path()],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[JoinRequestResponse]:
    """
    Reject a join request.

    Args:
        request_id: The join request's unique identifier.
        user: Authenticated user (team owner).
        service: Team service.

    Returns:
        BaseResponse[JoinRequestResponse]: Updated join request data.
    """
    return BaseResponse(data=await service.reject_join_request(request_id, user))


@router.get(
    "/join-requests/my",
    status_code=status.HTTP_200_OK,
    name="list my join requests",
    description="List My Join Requests",
    operation_id="list_my_join_requests",
)
async def list_my_join_requests(
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[JoinRequestListResponse]:
    """
    List all join requests created by the user.

    Args:
        user: Authenticated user.
        service: Team service.

    Returns:
        BaseResponse[JoinRequestListResponse]: List of join requests.
    """
    join_requests = await service.list_my_join_requests(user)
    return BaseResponse(data=JoinRequestListResponse(join_requests=join_requests))


@router.get(
    "/join-request/{request_id}",
    status_code=status.HTTP_200_OK,
    name="get join request",
    description="Get Join Request",
    operation_id="get_join_request",
)
async def get_join_request(
    request_id: Annotated[UUID, Path()],
    user: Annotated[UserModel, Depends(HasPermission(RoleType.USER))],
    service: Annotated[TeamService, Depends()],
) -> BaseResponse[JoinRequestResponse]:
    """
    Get join request details by ID.

    Args:
        request_id: The join request's unique identifier.
        user: Authenticated user.
        service: Team service.

    Returns:
        BaseResponse[JoinRequestResponse]: Join request data.
    """
    return BaseResponse(data=await service.get_join_request_by_id(request_id, user))
