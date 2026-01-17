from enum import StrEnum


class RoleType(StrEnum):
    """
    Enumeration of user role types.

    Defines different roles that users can have in the system, including:
    - ADMIN: Administrator role.
    - STAFF: Staff role.
    - USER: Regular user role.
    - ANY: Represents any role.
    - OPTIONAL: Represents an optional role.

    These roles are represented as strings for convenience.

    Attributes:
        ADMIN: Administrator role.
        STAFF: Staff role.
        USER: Regular user role.
        ANY: Represents any role.
        OPTIONAL: Represents an optional role.
    """

    ADMIN = "ADMIN"
    STAFF = "STAFF"
    USER = "USER"
    ANY = "ANY"
    OPTIONAL = "OPTIONAL"


class TeamRole(StrEnum):
    """
    Enumeration of team role types.

    Defines different roles that users can have within a team:
    - OWNER: Creator of the team, highest authority.
    - ADMIN: Elevated privileges inside the team.
    - MEMBER: Normal team participant.

    Attributes:
        OWNER: Owner role with full control.
        ADMIN: Admin role with elevated privileges.
        MEMBER: Member role with read-only access.
    """

    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class JoinRequestStatus(StrEnum):
    """
    Enumeration of join request status types.

    Defines different statuses for team join requests:
    - PENDING: Request is awaiting owner approval.
    - APPROVED: Request has been approved by owner.
    - DECLINED: Request has been rejected by owner.

    Attributes:
        PENDING: Request is pending approval.
        APPROVED: Request has been approved.
        DECLINED: Request has been declined.
    """

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


class TeamStatus(StrEnum):
    """
    Enumeration of team status types.

    Defines different statuses for teams:
    - ACTIVE: Team is active and operational.
    - DELETED: Team is soft-deleted (not shown in lists).

    Attributes:
        ACTIVE: Team is active.
        DELETED: Team is deleted (soft delete).
    """

    ACTIVE = "ACTIVE"
    DELETED = "DELETED"
