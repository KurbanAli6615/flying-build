from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test.utils.api_client import APIClient
    from test.utils.encryption import EncryptionHelper


async def prepare_signin_payload(
    email: str,
    password: str,
    api_client: "APIClient",
    encryption_helper: "EncryptionHelper",
) -> dict[str, str]:
    """
    Prepare encrypted sign-in payload.

    Args:
        email: User email
        password: User password
        api_client: API client instance
        encryption_helper: Encryption helper instance

    Returns:
        dict: Encrypted request payload with keys: encrypted_data, encrypted_key, iv
    """
    data = {"email": email, "password": password}

    return await encryption_helper.prepare_encrypted_request(data, api_client)


async def prepare_user_creation_payload(
    user_data: dict, api_client: "APIClient", encryption_helper: "EncryptionHelper"
) -> dict[str, str]:
    """
    Prepare encrypted user creation payload.

    Args:
        user_data: User data dictionary with fields:
            - name
            - username
            - email
            - country_code
            - phone
            - password
        api_client: API client instance
        encryption_helper: Encryption helper instance

    Returns:
        dict: Encrypted request payload with keys: encrypted_data, encrypted_key, iv
    """
    return await encryption_helper.prepare_encrypted_request(user_data, api_client)


def extract_auth_tokens(response_data: dict) -> dict[str, str]:
    """
    Extract authentication tokens from sign-in response.

    Args:
        response_data: Response data dictionary from sign-in endpoint

    Returns:
        dict: Dictionary with access_token and refresh_token
    """
    data = response_data.get("data", {})
    return {
        "access_token": data.get("accessToken", ""),
        "refresh_token": data.get("refreshToken", ""),
    }


def extract_user_data(response_data: dict) -> dict:
    """
    Extract user data from get-self response.

    Args:
        response_data: Response data dictionary from get-self endpoint

    Returns:
        dict: User data dictionary
    """
    return response_data.get("data", {})
