from apps.user.schemas import BaseUserResponse


class AdminListUsersResponse(BaseUserResponse):
    """
    Response object for listing users in the admin interface.

    Inherits from BaseUserResponse and includes additional fields specific to listing users
    in the admin interface.

    Attributes:
        email (str): The email address of the user.
        phone (str): The phone number of the user.
    """

    email: str
    phone: str
