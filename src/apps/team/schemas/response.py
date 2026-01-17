from datetime import datetime
from uuid import UUID

from core.types import JoinRequestStatus, TeamRole
from core.utils import CamelCaseModel


class TeamResponse(CamelCaseModel):
    """
    Team response schema.

    Attributes:
        id (UUID): The team's unique identifier.
        owner_id (UUID): The ID of the team owner.
        name (str): The name of the team.
        description (str | None): The description of the team.
        team_code (str): The unique team code.
        is_active (bool): Whether the team is active.
        role (TeamRole): The current user's role in the team.
        created_by (str): Name of the team creator. Shows "You" if current user is owner.
        created_at (datetime): When the team was created.
        member_count (int): The number of members in the team.
    """

    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    team_code: str
    is_active: bool
    role: TeamRole
    created_by: str
    created_at: datetime
    member_count: int


class TeamMemberResponse(CamelCaseModel):
    """
    Team member response schema.

    Attributes:
        user_id (UUID): The user's unique identifier.
        name (str): The user's name.
        username (str): The user's username.
        email (str): The user's email.
        role (TeamRole): The user's role in the team.
    """

    user_id: UUID
    name: str
    username: str
    email: str
    role: TeamRole


class TeamMemberListResponse(CamelCaseModel):
    """
    Team member list response schema.

    Attributes:
        members (list[TeamMemberResponse]): List of team members.
    """

    members: list[TeamMemberResponse]


class TeamListResponse(CamelCaseModel):
    """
    Team list response schema.

    Attributes:
        teams (list[TeamResponse]): List of teams.
    """

    teams: list[TeamResponse]


class JoinRequestResponse(CamelCaseModel):
    """
    Join request response schema.

    Attributes:
        id (UUID): The join request's unique identifier.
        team_id (UUID): The ID of the team.
        team_name (str): The name of the team.
        requested_by (UUID): The ID of the user who requested to join.
        requester_name (str): The name of the requester.
        requester_email (str): The email of the requester.
        status (JoinRequestStatus): The status of the request.
        reviewed_by (UUID | None): The ID of the user who reviewed the request.
        reviewer_name (str | None): The name of the reviewer.
        reviewed_at (datetime | None): When the request was reviewed.
        created_at (datetime): When the request was created.
    """

    id: UUID
    team_id: UUID
    team_name: str
    requested_by: UUID
    requester_name: str
    requester_email: str
    status: JoinRequestStatus
    reviewed_by: UUID | None
    reviewer_name: str | None
    reviewed_at: datetime | None
    created_at: datetime


class JoinRequestListResponse(CamelCaseModel):
    """
    Join request list response schema.

    Attributes:
        join_requests (list[JoinRequestResponse]): List of join requests.
    """

    join_requests: list[JoinRequestResponse]
