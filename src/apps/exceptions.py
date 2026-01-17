import constants
from core.exceptions import BadRequestError


class EmailRequiredException(BadRequestError):
    """
    Custom exception for email field required.
    """

    message = constants.EMAIL_FIELD_REQUIRED


class PasswordRequiredException(BadRequestError):
    """
    Custom exception for password field required.
    """

    message = constants.PASSWORD_FIELD_REQUIRED
