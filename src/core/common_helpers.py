import base64
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as crypto_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import constants
from apps.user.exceptions import (
    EmptyDescriptionException,
    InvalidEmailException,
    InvalidEncryptedData,
)
from apps.user.schemas import TokensResponse
from config import settings
from core.auth import access, admin_access, admin_refresh, refresh
from core.exceptions import InvalidRoleException
from core.types import RoleType


async def create_password():
    """
    Generate a URL-safe random password.
    
    Returns:
        str: A URL-safe random string suitable for use as a password.
    """
    return secrets.token_urlsafe(15)


async def create_tokens(user_id: UUID, role: RoleType) -> TokensResponse:
    """
    Create access and refresh tokens for a user based on their role.
    
    Parameters:
        user_id (UUID): The user's unique identifier to embed in token payloads.
        role (RoleType): The user's role; determines which encoder pair (user or admin) is used.
    
    Returns:
        TokensResponse: An object containing `access_token` and `refresh_token` strings.
    
    Raises:
        InvalidRoleException: If `role` is not `RoleType.USER` or `RoleType.ADMIN`.
    """
    if role == RoleType.USER:
        access_token = access.encode(
            payload={"id": str(user_id)}, expire_period=int(settings.ACCESS_TOKEN_EXP)
        )
        refresh_token = refresh.encode(
            payload={"id": str(user_id)}, expire_period=int(settings.REFRESH_TOKEN_EXP)
        )
    elif role == RoleType.ADMIN:
        access_token = admin_access.encode(
            payload={"id": str(user_id)}, expire_period=int(settings.ACCESS_TOKEN_EXP)
        )
        refresh_token = admin_refresh.encode(
            payload={"id": str(user_id)}, expire_period=int(settings.REFRESH_TOKEN_EXP)
        )
    else:
        raise InvalidRoleException

    return TokensResponse(access_token=access_token, refresh_token=refresh_token)


def validate_string_fields(values) -> dict:
    """
    Ensure string values in a mapping are not empty.
    
    Parameters:
        values (Mapping[str, Any]): Mapping of field names to their values to validate.
    
    Returns:
        dict: The original mapping of values.
    
    Raises:
        EmptyDescriptionException: If any value is a string that is empty or contains only whitespace.
    """
    for field_name, value in values.items():
        if isinstance(value, str) and not value.strip():
            raise EmptyDescriptionException(
                message=f"{field_name} must not be an empty string"
            )
    return values


async def decrypt(
    rsa_key: rsa.RSAPrivateKey,
    enc_data: str,
    encrypt_key: str,
    iv_input: str,
    time_check: bool = False,
    timeout: int = 5,
) -> bytes:
    """Decrypts the given encrypted data.

    :param enc_data: Encrypted Data
    :param encrypt_key: Encrypted Key
    :param iv_input: IV Input
    :param time_check: Whether to check the time of the encrypted data
    :param timeout: Timeout in seconds(5 by default)
    :return: Decrypted code
    """
    try:
        code_bytes = encrypt_key.encode("UTF-8")
        encoded_by = base64.b64decode(code_bytes)
        decrypted_key = rsa_key.decrypt(encoded_by, asym_padding.PKCS1v15()).decode()

        iv = base64.b64decode(iv_input)
        enc = base64.b64decode(enc_data)
        cipher = Cipher(
            algorithms.AES(decrypted_key.encode("utf-8")),
            modes.CBC(iv),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(enc) + decryptor.finalize()
        unpadder = crypto_padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        payload = json.loads(plaintext.decode())
        if time_check:
            exp = datetime.fromisoformat(payload.get("timestamp"))
            if exp is None:
                raise InvalidEncryptedData
            current_time = datetime.now(timezone.utc)
            if (current_time - exp) > timedelta(seconds=timeout):
                raise InvalidEncryptedData
        return plaintext
    except Exception:
        raise InvalidEncryptedData


def validate_email(email: str) -> str | None:
    """
    Validate the format of an email address.
    :param email: The email address to be validated.
    :return: The validated email address.
    """

    if not re.match(constants.EMAIL_REGEX, email):
        raise InvalidEmailException

    if not isinstance(email, str) and email is not None:
        raise InvalidEmailException

    return email