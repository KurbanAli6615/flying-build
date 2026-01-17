from uuid import UUID

from core.utils import CamelCaseModel


class TokensResponse(CamelCaseModel):
    """
    Response object for tokens.
    """

    access_token: str
    refresh_token: str


class BaseUserResponse(CamelCaseModel):
    """
    Base response object for user information.

    Attributes:
        id (UUID): The user's unique identifier.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
    """

    id: UUID
    name: str
    username: str
    email: str
    country_code: str
    phone: str
    role: str


class PublicKeyResponse(CamelCaseModel):
    """
    Response object for public key.
    """

    public_key: str
