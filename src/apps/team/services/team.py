from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from apps.team.exception import (
    CannotModifyOwner,
    DuplicateJoinRequest,
    InvalidTeamCode,
    JoinRequestNotFound,
    TeamDeactivated,
    TeamMemberNotFound,
    TeamNotFound,
    UnauthorizedTeamAccess,
    UserAlreadyMember,
)
from apps.team.schemas.request import (
    CreateTeamRequest,
    JoinTeamRequest,
    PromoteToAdminRequest,
    ToggleTeamActiveRequest,
    UpdateTeamRequest,
)
from apps.team.schemas.response import (
    JoinRequestResponse,
    TeamMemberResponse,
    TeamResponse,
)
from core.common_helpers import generate_team_code
from core.db import db_session
from core.types import JoinRequestStatus, TeamRole
from core.utils.schema import SuccessResponse
from models import JoinRequestModel, TeamMemberModel, TeamModel, UserModel


class TeamService:
    """
    Service with methods to handle team operations.

    This service provides methods for creating teams, managing team members,
    handling join requests, and performing team-related operations.
    """

    def __init__(self, session: Annotated[AsyncSession, Depends(db_session)]):
        """
        Create a TeamService bound to a database session.

        Parameters:
            session (AsyncSession): Database session injected via FastAPI
                Depends(db_session) used for database operations.
        """
        self.session = session

    #  MARK: - Create Team
    # *======================================== Create Team ========================================
    async def create_team(
        self, request: Request, user: UserModel, data: CreateTeamRequest
    ) -> TeamResponse:
        """
        Create a new team using data from the request on behalf of the given user.

        Parameters:
            request (Request): HTTP request containing the team creation payload.
            user (UserModel): User performing the action; used for ownership.
            data (CreateTeamRequest): Team creation data.

        Returns:
            TeamResponse: Created team data with role.

        Raises:
            TeamAlreadyExists: If team code collision occurs (unlikely).
        """
        team_code = await generate_team_code(self.session)

        team = TeamModel(
            owner_id=user.id,
            name=data.name,
            description=data.description,
            team_code=team_code,
            is_active=True,
        )
        self.session.add(team)
        await self.session.flush()

        team_member = TeamMemberModel(
            team_id=team.id, user_id=user.id, role=TeamRole.OWNER
        )
        self.session.add(team_member)

        return TeamResponse(
            id=team.id,
            owner_id=team.owner_id,
            name=team.name,
            description=team.description,
            team_code=team.team_code,
            is_active=team.is_active,
            role=TeamRole.OWNER,
            created_by="You",
            created_at=team.created_at,
        )

    #  MARK: - List My Teams
    # *======================================== List My Teams ========================================
    async def list_my_teams(self, user: UserModel) -> list[TeamResponse]:
        """
        List all teams where the user is a member.

        Parameters:
            user (UserModel): The authenticated user.

        Returns:
            list[TeamResponse]: List of teams with role,
                ordered by created_at ascending (oldest first).
        """
        team_members = await self.session.scalars(
            select(TeamMemberModel)
            .options(joinedload(TeamMemberModel.team))
            .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
            .where(TeamMemberModel.user_id == user.id)
            .order_by(TeamModel.created_at.asc())
        )

        team_members_list = list(team_members)
        teams = []
        owner_ids = set()
        for member in team_members_list:
            team = member.team
            # Filter: if is_active=False, show only to OWNER
            if not team.is_active and member.role != TeamRole.OWNER:
                continue
            owner_ids.add(team.owner_id)

        # Load all owners in one query
        owners = {}
        if owner_ids:
            owner_users = await self.session.scalars(
                select(UserModel)
                .options(load_only(UserModel.id, UserModel.name))
                .where(UserModel.id.in_(owner_ids))
            )
            owners = {owner.id: owner.name for owner in owner_users}

        for member in team_members_list:
            team = member.team
            # Filter: if is_active=False, show only to OWNER
            if not team.is_active and member.role != TeamRole.OWNER:
                continue

            created_by = (
                "You"
                if member.role == TeamRole.OWNER
                else owners.get(team.owner_id, "")
            )

            teams.append(
                TeamResponse(
                    id=team.id,
                    owner_id=team.owner_id,
                    name=team.name,
                    description=team.description,
                    team_code=team.team_code,
                    is_active=team.is_active,
                    role=member.role,
                    created_by=created_by,
                    created_at=team.created_at,
                )
            )

        return teams

    #  MARK: - Get Team By ID
    # *======================================== Get Team By ID ========================================
    async def get_team_by_id(self, team_id: UUID, user: UserModel) -> TeamResponse:
        """
        Get team details by ID.

        Parameters:
            team_id (UUID): The team's unique identifier.
            user (UserModel): The authenticated user.

        Returns:
            TeamResponse: Team data with role.

        Raises:
            TeamNotFound: If team is not found.
            UnauthorizedTeamAccess: If user is not a team member.
            TeamDeactivated: If team is deactivated and user is MEMBER.
        """
        team = await self.session.scalar(
            select(TeamModel)
            .options(load_only(TeamModel.id, TeamModel.owner_id, TeamModel.name))
            .where(TeamModel.id == team_id)
        )

        if not team:
            raise TeamNotFound

        team_member = await self.session.scalar(
            select(TeamMemberModel).where(
                TeamMemberModel.team_id == team_id, TeamMemberModel.user_id == user.id
            )
        )

        if not team_member:
            raise UnauthorizedTeamAccess

        # Reload team with all fields
        team = await self.session.scalar(
            select(TeamModel).where(TeamModel.id == team_id)
        )

        # Check if team is deactivated and user is MEMBER
        if not team.is_active and team_member.role == TeamRole.MEMBER:
            raise TeamDeactivated

        # Get owner name
        owner = await self.session.scalar(
            select(UserModel)
            .options(load_only(UserModel.id, UserModel.name))
            .where(UserModel.id == team.owner_id)
        )
        created_by = (
            "You"
            if team_member.role == TeamRole.OWNER
            else (owner.name if owner else "")
        )

        return TeamResponse(
            id=team.id,
            owner_id=team.owner_id,
            name=team.name,
            description=team.description,
            team_code=team.team_code,
            is_active=team.is_active,
            role=team_member.role,
            created_by=created_by,
            created_at=team.created_at,
        )

    #  MARK: - Update Team
    # *======================================== Update Team ========================================
    async def update_team(
        self, team_id: UUID, user: UserModel, data: UpdateTeamRequest
    ) -> TeamResponse:
        """
        Update team name or description.

        Parameters:
            team_id (UUID): The team's unique identifier.
            user (UserModel): The authenticated user.
            data (UpdateTeamRequest): Update data.

        Returns:
            TeamResponse: Updated team data.

        Raises:
            TeamNotFound: If team is not found.
            UnauthorizedTeamAccess: If user is not OWNER or ADMIN.
        """
        team = await self.session.scalar(
            select(TeamModel).where(TeamModel.id == team_id)
        )

        if not team:
            raise TeamNotFound

        team_member = await self._validate_team_role(
            team_id, user.id, [TeamRole.OWNER, TeamRole.ADMIN]
        )

        if data.name is not None:
            team.name = data.name
        if data.description is not None:
            team.description = data.description

        # Get owner name
        owner = await self.session.scalar(
            select(UserModel)
            .options(load_only(UserModel.id, UserModel.name))
            .where(UserModel.id == team.owner_id)
        )
        created_by = (
            "You"
            if team_member.role == TeamRole.OWNER
            else (owner.name if owner else "")
        )

        return TeamResponse(
            id=team.id,
            owner_id=team.owner_id,
            name=team.name,
            description=team.description,
            team_code=team.team_code,
            is_active=team.is_active,
            role=team_member.role,
            created_by=created_by,
            created_at=team.created_at,
        )

    #  MARK: - Toggle Team Active Status
    # *======================================== Toggle Team Active Status ========================================
    async def toggle_team_active_status(
        self, team_id: UUID, owner: UserModel, data: ToggleTeamActiveRequest
    ) -> SuccessResponse:
        """
        Toggle team active/deactive status.

        Only the team owner can activate or deactivate the team.

        Parameters:
            team_id (UUID): The team's unique identifier.
            owner (UserModel): The team owner.
            data (ToggleTeamActiveRequest): Toggle data with is_active flag.

        Returns:
            SuccessResponse: Success message.

        Raises:
            TeamNotFound: If team is not found.
            UnauthorizedTeamAccess: If user is not OWNER.
        """
        team = await self.session.scalar(
            select(TeamModel)
            .options(load_only(TeamModel.id, TeamModel.is_active))
            .where(TeamModel.id == team_id)
        )

        if not team:
            raise TeamNotFound

        await self._validate_team_role(team_id, owner.id, [TeamRole.OWNER])

        team.is_active = data.is_active

        return SuccessResponse()

    #  MARK: - Delete Team
    # *======================================== Delete Team ========================================
    async def delete_team(self, team_id: UUID, owner: UserModel) -> SuccessResponse:
        """
        Delete a team (soft delete by setting is_active=False).

        Only the team owner can delete the team.

        Parameters:
            team_id (UUID): The team's unique identifier.
            owner (UserModel): The team owner.

        Returns:
            SuccessResponse: Success message.

        Raises:
            TeamNotFound: If team is not found.
            UnauthorizedTeamAccess: If user is not OWNER.
        """
        team = await self.session.scalar(
            select(TeamModel).where(TeamModel.id == team_id)
        )

        if not team:
            raise TeamNotFound

        await self._validate_team_role(team_id, owner.id, [TeamRole.OWNER])

        team.is_active = False

        return SuccessResponse()

    #  MARK: - List Team Members
    # *======================================== List Team Members ========================================
    async def list_team_members(
        self, team_id: UUID, user: UserModel
    ) -> list[TeamMemberResponse]:
        """
        List all team members with their roles.

        All team members (OWNER, ADMIN, MEMBER) can view the team members list.

        Parameters:
            team_id (UUID): The team's unique identifier.
            user (UserModel): The authenticated user.

        Returns:
            list[TeamMemberResponse]: List of team members.

        Raises:
            TeamNotFound: If team is not found.
            UnauthorizedTeamAccess: If user is not a team member.
        """
        team = await self.session.scalar(
            select(TeamModel)
            .options(load_only(TeamModel.id))
            .where(TeamModel.id == team_id)
        )

        if not team:
            raise TeamNotFound

        # Validate user is a team member (any role)
        await self._validate_team_membership(team_id, user.id)

        team_members = await self.session.scalars(
            select(TeamMemberModel)
            .options(joinedload(TeamMemberModel.user))
            .where(TeamMemberModel.team_id == team_id)
        )

        return [
            TeamMemberResponse(
                user_id=member.user_id,
                name=member.user.name,
                username=member.user.username,
                email=member.user.email,
                role=member.role,
            )
            for member in team_members
        ]

    #  MARK: - Promote To Admin
    # *======================================== Promote To Admin ========================================
    async def promote_to_admin(
        self, team_id: UUID, data: PromoteToAdminRequest, owner: UserModel
    ) -> SuccessResponse:
        """
        Promote a user to admin role.

        Parameters:
            team_id (UUID): The team's unique identifier.
            data (PromoteToAdminRequest): Promotion data with user_id.
            owner (UserModel): The team owner.

        Returns:
            SuccessResponse: Success message.

        Raises:
            TeamNotFound: If team is not found.
            UnauthorizedTeamAccess: If user is not OWNER.
            TeamMemberNotFound: If user is not a team member.
            CannotModifyOwner: If trying to modify owner role.
        """
        team = await self.session.scalar(
            select(TeamModel)
            .options(load_only(TeamModel.id))
            .where(TeamModel.id == team_id)
        )

        if not team:
            raise TeamNotFound

        await self._validate_team_role(team_id, owner.id, [TeamRole.OWNER])

        if data.user_id == owner.id:
            raise CannotModifyOwner

        team_member = await self.session.scalar(
            select(TeamMemberModel).where(
                TeamMemberModel.team_id == team_id,
                TeamMemberModel.user_id == data.user_id,
            )
        )

        if not team_member:
            raise TeamMemberNotFound

        if team_member.role == TeamRole.OWNER:
            raise CannotModifyOwner

        team_member.role = TeamRole.ADMIN

        return SuccessResponse()

    #  MARK: - Demote From Admin
    # *======================================== Demote From Admin ========================================
    async def demote_from_admin(
        self, team_id: UUID, user_id: UUID, owner: UserModel
    ) -> SuccessResponse:
        """
        Demote an admin to member role.

        Parameters:
            team_id (UUID): The team's unique identifier.
            user_id (UUID): The user to demote.
            owner (UserModel): The team owner.

        Returns:
            SuccessResponse: Success message.

        Raises:
            TeamNotFound: If team is not found.
            UnauthorizedTeamAccess: If user is not OWNER.
            TeamMemberNotFound: If user is not a team member.
            CannotModifyOwner: If trying to modify owner role.
        """
        team = await self.session.scalar(
            select(TeamModel)
            .options(load_only(TeamModel.id))
            .where(TeamModel.id == team_id)
        )

        if not team:
            raise TeamNotFound

        await self._validate_team_role(team_id, owner.id, [TeamRole.OWNER])

        if user_id == owner.id:
            raise CannotModifyOwner

        team_member = await self.session.scalar(
            select(TeamMemberModel).where(
                TeamMemberModel.team_id == team_id, TeamMemberModel.user_id == user_id
            )
        )

        if not team_member:
            raise TeamMemberNotFound

        if team_member.role == TeamRole.OWNER:
            raise CannotModifyOwner

        team_member.role = TeamRole.MEMBER

        return SuccessResponse()

    #  MARK: - Create Join Request
    # *======================================== Create Join Request ========================================
    async def create_join_request(
        self, data: JoinTeamRequest, user: UserModel
    ) -> JoinRequestResponse:
        """
        Create a join request using team code.

        Parameters:
            data (JoinTeamRequest): Join request data with team_code.
            user (UserModel): The authenticated user.

        Returns:
            JoinRequestResponse: Created join request data.

        Raises:
            InvalidTeamCode: If team code is invalid.
            DuplicateJoinRequest: If pending request already exists.
            UserAlreadyMember: If user is already a team member.
        """
        team = await self.session.scalar(
            select(TeamModel).where(TeamModel.team_code == data.team_code)
        )

        if not team:
            raise InvalidTeamCode

        # Check if user is already a member
        existing_member = await self.session.scalar(
            select(TeamMemberModel).where(
                TeamMemberModel.team_id == team.id, TeamMemberModel.user_id == user.id
            )
        )

        if existing_member:
            raise UserAlreadyMember

        # Check for duplicate pending request
        existing_request = await self.session.scalar(
            select(JoinRequestModel).where(
                JoinRequestModel.team_id == team.id,
                JoinRequestModel.requested_by == user.id,
                JoinRequestModel.status == JoinRequestStatus.PENDING,
            )
        )

        if existing_request:
            raise DuplicateJoinRequest

        join_request = JoinRequestModel(
            team_id=team.id, requested_by=user.id, status=JoinRequestStatus.PENDING
        )
        self.session.add(join_request)
        await self.session.flush()

        return JoinRequestResponse(
            id=join_request.id,
            team_id=join_request.team_id,
            team_name=team.name,
            requested_by=join_request.requested_by,
            requester_name=user.name,
            requester_email=user.email,
            status=join_request.status,
            reviewed_by=join_request.reviewed_by,
            reviewer_name=None,
            reviewed_at=join_request.reviewed_at,
            created_at=join_request.created_at,
        )

    #  MARK: - List Team Join Requests
    # *======================================== List Team Join Requests ========================================
    async def list_team_join_requests(
        self, team_id: UUID, owner: UserModel
    ) -> list[JoinRequestResponse]:
        """
        List all join requests for a team.

        Parameters:
            team_id (UUID): The team's unique identifier.
            owner (UserModel): The team owner.

        Returns:
            list[JoinRequestResponse]: List of join requests.

        Raises:
            TeamNotFound: If team is not found.
            UnauthorizedTeamAccess: If user is not OWNER.
        """
        team = await self.session.scalar(
            select(TeamModel)
            .options(load_only(TeamModel.id, TeamModel.name))
            .where(TeamModel.id == team_id)
        )

        if not team:
            raise TeamNotFound

        await self._validate_team_role(team_id, owner.id, [TeamRole.OWNER])

        join_requests = await self.session.scalars(
            select(JoinRequestModel)
            .options(
                joinedload(JoinRequestModel.requester),
                joinedload(JoinRequestModel.reviewer),
            )
            .where(JoinRequestModel.team_id == team_id)
        )

        return [
            JoinRequestResponse(
                id=req.id,
                team_id=req.team_id,
                team_name=team.name,
                requested_by=req.requested_by,
                requester_name=req.requester.name,
                requester_email=req.requester.email,
                status=req.status,
                reviewed_by=req.reviewed_by,
                reviewer_name=req.reviewer.name if req.reviewer else None,
                reviewed_at=req.reviewed_at,
                created_at=req.created_at,
            )
            for req in join_requests
        ]

    #  MARK: - Approve Join Request
    # *======================================== Approve Join Request ========================================
    async def approve_join_request(
        self, request_id: UUID, owner: UserModel
    ) -> JoinRequestResponse:
        """
        Approve a join request and add user as team member.

        Parameters:
            request_id (UUID): The join request's unique identifier.
            owner (UserModel): The team owner.

        Returns:
            JoinRequestResponse: Updated join request data.

        Raises:
            JoinRequestNotFound: If join request is not found.
            UnauthorizedTeamAccess: If user is not OWNER.
            UserAlreadyMember: If user is already a team member.
        """
        join_request = await self.session.scalar(
            select(JoinRequestModel)
            .options(joinedload(JoinRequestModel.team))
            .where(JoinRequestModel.id == request_id)
        )

        if not join_request:
            raise JoinRequestNotFound

        await self._validate_team_role(join_request.team_id, owner.id, [TeamRole.OWNER])

        # Check if user is already a member
        existing_member = await self.session.scalar(
            select(TeamMemberModel).where(
                TeamMemberModel.team_id == join_request.team_id,
                TeamMemberModel.user_id == join_request.requested_by,
            )
        )

        if existing_member:
            raise UserAlreadyMember

        join_request.status = JoinRequestStatus.APPROVED
        join_request.reviewed_by = owner.id
        join_request.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)

        # Create team member
        team_member = TeamMemberModel(
            team_id=join_request.team_id,
            user_id=join_request.requested_by,
            role=TeamRole.MEMBER,
        )
        self.session.add(team_member)

        await self.session.flush()

        # Reload with relationships
        join_request = await self.session.scalar(
            select(JoinRequestModel)
            .options(
                joinedload(JoinRequestModel.team),
                joinedload(JoinRequestModel.requester),
                joinedload(JoinRequestModel.reviewer),
            )
            .where(JoinRequestModel.id == request_id)
        )

        return JoinRequestResponse(
            id=join_request.id,
            team_id=join_request.team_id,
            team_name=join_request.team.name,
            requested_by=join_request.requested_by,
            requester_name=join_request.requester.name,
            requester_email=join_request.requester.email,
            status=join_request.status,
            reviewed_by=join_request.reviewed_by,
            reviewer_name=join_request.reviewer.name if join_request.reviewer else None,
            reviewed_at=join_request.reviewed_at,
            created_at=join_request.created_at,
        )

    #  MARK: - Reject Join Request
    # *======================================== Reject Join Request ========================================
    async def reject_join_request(
        self, request_id: UUID, owner: UserModel
    ) -> JoinRequestResponse:
        """
        Reject a join request.

        Parameters:
            request_id (UUID): The join request's unique identifier.
            owner (UserModel): The team owner.

        Returns:
            JoinRequestResponse: Updated join request data.

        Raises:
            JoinRequestNotFound: If join request is not found.
            UnauthorizedTeamAccess: If user is not OWNER.
        """
        join_request = await self.session.scalar(
            select(JoinRequestModel)
            .options(joinedload(JoinRequestModel.team))
            .where(JoinRequestModel.id == request_id)
        )

        if not join_request:
            raise JoinRequestNotFound

        await self._validate_team_role(join_request.team_id, owner.id, [TeamRole.OWNER])

        join_request.status = JoinRequestStatus.DECLINED
        join_request.reviewed_by = owner.id
        join_request.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.session.flush()

        # Reload with relationships
        join_request = await self.session.scalar(
            select(JoinRequestModel)
            .options(
                joinedload(JoinRequestModel.team),
                joinedload(JoinRequestModel.requester),
                joinedload(JoinRequestModel.reviewer),
            )
            .where(JoinRequestModel.id == request_id)
        )

        return JoinRequestResponse(
            id=join_request.id,
            team_id=join_request.team_id,
            team_name=join_request.team.name,
            requested_by=join_request.requested_by,
            requester_name=join_request.requester.name,
            requester_email=join_request.requester.email,
            status=join_request.status,
            reviewed_by=join_request.reviewed_by,
            reviewer_name=join_request.reviewer.name if join_request.reviewer else None,
            reviewed_at=join_request.reviewed_at,
            created_at=join_request.created_at,
        )

    #  MARK: - List My Join Requests
    # *======================================== List My Join Requests ========================================
    async def list_my_join_requests(self, user: UserModel) -> list[JoinRequestResponse]:
        """
        List all join requests created by the user.

        Parameters:
            user (UserModel): The authenticated user.

        Returns:
            list[JoinRequestResponse]: List of join requests.
        """
        join_requests = await self.session.scalars(
            select(JoinRequestModel)
            .options(
                joinedload(JoinRequestModel.team),
                joinedload(JoinRequestModel.requester),
                joinedload(JoinRequestModel.reviewer),
            )
            .where(JoinRequestModel.requested_by == user.id)
        )

        return [
            JoinRequestResponse(
                id=req.id,
                team_id=req.team_id,
                team_name=req.team.name,
                requested_by=req.requested_by,
                requester_name=req.requester.name,
                requester_email=req.requester.email,
                status=req.status,
                reviewed_by=req.reviewed_by,
                reviewer_name=req.reviewer.name if req.reviewer else None,
                reviewed_at=req.reviewed_at,
                created_at=req.created_at,
            )
            for req in join_requests
        ]

    #  MARK: - Get Join Request By ID
    # *======================================== Get Join Request By ID ========================================
    async def get_join_request_by_id(
        self, request_id: UUID, user: UserModel
    ) -> JoinRequestResponse:
        """
        Get join request details by ID.

        Parameters:
            request_id (UUID): The join request's unique identifier.
            user (UserModel): The authenticated user.

        Returns:
            JoinRequestResponse: Join request data.

        Raises:
            JoinRequestNotFound: If join request is not found.
            UnauthorizedTeamAccess: If user is not OWNER or requester.
        """
        join_request = await self.session.scalar(
            select(JoinRequestModel)
            .options(
                joinedload(JoinRequestModel.team),
                joinedload(JoinRequestModel.requester),
                joinedload(JoinRequestModel.reviewer),
            )
            .where(JoinRequestModel.id == request_id)
        )

        if not join_request:
            raise JoinRequestNotFound

        # Check if user is owner or requester
        is_requester = join_request.requested_by == user.id
        is_owner = False

        if not is_requester:
            team_member = await self.session.scalar(
                select(TeamMemberModel).where(
                    TeamMemberModel.team_id == join_request.team_id,
                    TeamMemberModel.user_id == user.id,
                    TeamMemberModel.role == TeamRole.OWNER,
                )
            )
            is_owner = team_member is not None

        if not is_requester and not is_owner:
            raise UnauthorizedTeamAccess

        return JoinRequestResponse(
            id=join_request.id,
            team_id=join_request.team_id,
            team_name=join_request.team.name,
            requested_by=join_request.requested_by,
            requester_name=join_request.requester.name,
            requester_email=join_request.requester.email,
            status=join_request.status,
            reviewed_by=join_request.reviewed_by,
            reviewer_name=join_request.reviewer.name if join_request.reviewer else None,
            reviewed_at=join_request.reviewed_at,
            created_at=join_request.created_at,
        )

    #  MARK: - Helper Methods
    # *======================================== Helper Methods ========================================
    async def _get_user_team_role(
        self, team_id: UUID, user_id: UUID
    ) -> TeamRole | None:
        """
        Get user's role in a team.

        Parameters:
            team_id (UUID): The team's unique identifier.
            user_id (UUID): The user's unique identifier.

        Returns:
            TeamRole | None: The user's role or None if not a member.
        """
        team_member = await self.session.scalar(
            select(TeamMemberModel).where(
                TeamMemberModel.team_id == team_id, TeamMemberModel.user_id == user_id
            )
        )

        return team_member.role if team_member else None

    async def _validate_team_membership(
        self, team_id: UUID, user_id: UUID
    ) -> TeamMemberModel:
        """
        Validate that user is a team member.

        Parameters:
            team_id (UUID): The team's unique identifier.
            user_id (UUID): The user's unique identifier.

        Returns:
            TeamMemberModel: The team membership record.

        Raises:
            UnauthorizedTeamAccess: If user is not a team member.
        """
        team_member = await self.session.scalar(
            select(TeamMemberModel).where(
                TeamMemberModel.team_id == team_id, TeamMemberModel.user_id == user_id
            )
        )

        if not team_member:
            raise UnauthorizedTeamAccess

        return team_member

    async def _validate_team_role(
        self, team_id: UUID, user_id: UUID, required_roles: list[TeamRole]
    ) -> TeamMemberModel:
        """
        Validate that user has one of the required roles in the team.

        Parameters:
            team_id (UUID): The team's unique identifier.
            user_id (UUID): The user's unique identifier.
            required_roles (list[TeamRole]): List of allowed roles.

        Returns:
            TeamMemberModel: The team membership record.

        Raises:
            UnauthorizedTeamAccess: If user is not a member or lacks required role.
        """
        team_member = await self._validate_team_membership(team_id, user_id)

        if team_member.role not in required_roles:
            raise UnauthorizedTeamAccess

        return team_member
