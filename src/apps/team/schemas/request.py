from uuid import UUID

from core.utils import CamelCaseModel


class CreateTeamRequest(CamelCaseModel):
    """
    Create team request schema.

    Attributes:
        name (str): The name of the team.
        description (str | None): Optional description of the team.
    """

    name: str
    description: str | None = None


class UpdateTeamRequest(CamelCaseModel):
    """
    Update team request schema.

    Attributes:
        name (str | None): Optional new name for the team.
        description (str | None): Optional new description for the team.
    """

    name: str | None = None
    description: str | None = None


class JoinTeamRequest(CamelCaseModel):
    """
    Join team request schema.

    Attributes:
        team_code (str): The unique team code to join.
    """

    team_code: str


class PromoteToAdminRequest(CamelCaseModel):
    """
    Promote user to admin request schema.

    Attributes:
        user_id (UUID): The ID of the user to promote to admin.
    """

    user_id: UUID


class ToggleTeamActiveRequest(CamelCaseModel):
    """
    Toggle team active status request schema.

    Attributes:
        is_active (bool): Whether the team should be active or deactivated.
    """

    is_active: bool
