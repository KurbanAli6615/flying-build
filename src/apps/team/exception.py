import constants
from core.exceptions import (
    AlreadyExistsError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
)


class TeamNotFound(NotFoundError):
    """
    Exception raised when team is not found.
    """

    message = constants.TEAM_NOT_FOUND


class TeamAlreadyExists(AlreadyExistsError):
    """
    Exception raised when team with this code already exists.
    """

    message = constants.TEAM_ALREADY_EXISTS


class TeamMemberNotFound(NotFoundError):
    """
    Exception raised when team member is not found.
    """

    message = constants.TEAM_MEMBER_NOT_FOUND


class UnauthorizedTeamAccess(ForbiddenError):
    """
    Exception raised when user has unauthorized access to team.
    """

    message = constants.UNAUTHORIZED_TEAM_ACCESS


class JoinRequestNotFound(NotFoundError):
    """
    Exception raised when join request is not found.
    """

    message = constants.JOIN_REQUEST_NOT_FOUND


class DuplicateJoinRequest(AlreadyExistsError):
    """
    Exception raised when pending join request already exists.
    """

    message = constants.DUPLICATE_JOIN_REQUEST


class InvalidTeamCode(BadRequestError):
    """
    Exception raised when team code is invalid.
    """

    message = constants.INVALID_TEAM_CODE


class CannotModifyOwner(BadRequestError):
    """
    Exception raised when trying to modify owner role.
    """

    message = constants.CANNOT_MODIFY_OWNER


class UserAlreadyMember(AlreadyExistsError):
    """
    Exception raised when user is already a team member.
    """

    message = constants.USER_ALREADY_MEMBER


class TeamDeactivated(BadRequestError):
    """
    Exception raised when trying to access a deactivated team.
    """

    message = constants.TEAM_DEACTIVATED
