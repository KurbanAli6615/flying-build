import constants
from core.exceptions import (
    BadRequestError,
    CustomException,
    NotFoundError,
    UnauthorizedError,
    UnprocessableEntityError,
)


class DuplicateEmailException(CustomException):
    """
    Custom exception for email duplication.
    """

    message = constants.DUPLICATE_EMAIL


class DuplicatePhoneException(CustomException):
    """
    Custom exception for phone number duplication.
    """

    message = constants.DUPLICATE_PHONE


class DuplicateUsernameException(CustomException):
    """
    Custom exception for username duplication.
    """

    message = constants.DUPLICATE_USERNAME


class InvalidCredentialsException(UnauthorizedError):
    """
    Custom exception to show a generic error message.
    """

    message = constants.INVALID_CREDS


class UserNotFoundException(NotFoundError):
    """
    Custom exception to show a generic error message.
    """

    message = constants.USER_NOT_FOUND


class EmptyDescriptionException(UnprocessableEntityError):
    """
    Custom exception for issue with the notes create empty description.
    """

    message = constants.DESCRIPTION


class InvalidEncryptedData(BadRequestError):
    """
    Custom exception for User already assigned error.
    """

    message = constants.INVALID_ENCRYPTED_DATA


class WeakPasswordException(BadRequestError):
    """
    Custom exception for User already assigned error.
    """

    message = constants.WEAK_PASSWORD


class InvalidPhoneFormatException(BadRequestError):
    """
    Custom exception for invalid phone number format.
    """

    message = constants.INVALID_PHONE_NUMBER


class InvalidEmailException(BadRequestError):
    """
    Custom exception for invalid email.
    """

    message = constants.INVALID_EMAIL


class InvalidRequestException(BadRequestError):
    """
    Custom exception for invalid request.
    """

    message = constants.INVALID_REQUEST


class InvalidUserNameException(BadRequestError):
    """
    Custom exception for invalid username.
    """

    message = constants.INVALID_USERNAME


class InvalidCountryCodeException(BadRequestError):
    """
    Custom exception for invalid country code.
    """

    message = constants.INVALID_COUNTRY_CODE


class InvalidNameException(BadRequestError):
    """
    Custom exception for invalid name.
    """

    message = constants.INVALID_NAME


class InvalidIsActiveException(BadRequestError):
    """
    Custom exception for invalid is active.
    """

    message = constants.INVALID_IS_ACTIVE


class InvalidRoleValueException(BadRequestError):
    """
    Custom exception for invalid role value.
    """

    message = constants.INVALID_ROLE_VALUE


class InvalidRequestError(BadRequestError):
    """
    Custom exception for invalid request.
    """

    message = constants.INVALID_REQUEST


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


class UserNotActiveException(BadRequestError):
    """
    Custom exception for user not active.
    """

    message = constants.USER_NOT_ACTIVE
