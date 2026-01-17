import json
import re
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

import constants
from apps.user.exceptions import (
    DuplicateEmailException,
    DuplicatePhoneException,
    DuplicateUsernameException,
    EmailRequiredException,
    InvalidCountryCodeException,
    InvalidCredentialsException,
    InvalidEmailException,
    InvalidNameException,
    InvalidPhoneFormatException,
    InvalidUserNameException,
    PasswordRequiredException,
    UserNotActiveException,
    UserNotFoundException,
    WeakPasswordException,
)
from apps.user.schemas import BaseUserResponse, PublicKeyResponse, TokensResponse
from config import settings
from constants.regex import COUNTRY_CODE, EMAIL_REGEX, NAME, PHONE_REGEX, USERNAME
from core.common_helpers import create_tokens, decrypt
from core.db import db_session
from core.types import RoleType
from core.utils.hashing import hash_password, verify_password
from core.utils.password import strong_password
from core.utils.schema import SuccessResponse
from models import UserModel


class UserService:
    """
    Service with methods to handle user authentication and information.

    This service provides methods for creating users, logging in, and retrieving user information.
    """

    def __init__(self, session: Annotated[AsyncSession, Depends(db_session)]) -> None:
        """
        Initialize AuthService with a database session
        This method also calls a database connection which is injected here.

        Args:
            session (AsyncSession): An asynchronous database connection.
        """
        self.session = session

    #  MARK: - Get Self
    # *======================================== Get Self ========================================
    async def get_self(self, user_id: UUID) -> BaseUserResponse:
        """
        Retrieve the current user's public profile by user ID.

        Parameters:
            user_id (UUID): The UUID of the user to retrieve.

        Returns:
            BaseUserResponse: Object containing id, email, name, username, country_code, phone, and role.

        Raises:
            UserNotFoundException: If no user exists with the given ID.
            UserNotActiveException: If the user exists but is not active.
        """
        user = await self.session.scalar(
            select(UserModel)
            .options(
                load_only(
                    UserModel.id,
                    UserModel.email,
                    UserModel.name,
                    UserModel.username,
                    UserModel.country_code,
                    UserModel.phone,
                    UserModel.is_active,
                    UserModel.role,
                )
            )
            .where(UserModel.id == user_id)
        )

        if not user:
            raise UserNotFoundException

        if not user.is_active:
            raise UserNotActiveException

        return BaseUserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            username=user.username,
            country_code=user.country_code,
            phone=user.phone,
            role=user.role,
        )

    #  MARK: - Login User
    # *======================================== Login User ========================================
    async def login_user(
        self, request: Request, encrypted_data: str, encrypted_key: str, iv: str
    ) -> TokensResponse:
        """
        Authenticate a user from RSA-encrypted credentials and return issued authentication tokens.

        Decrypts the provided payload to obtain email and password, validates presence of both fields, verifies credentials, and returns the generated tokens.

        Parameters:
            encrypted_data (str): RSA-encrypted JSON payload containing `email` and `password`.
            encrypted_key (str): RSA-encrypted key used to encrypt the payload.
            iv (str): Initialization vector used during encryption.

        Returns:
            TokensResponse: Contains issued authentication tokens (e.g., `access_token` and `refresh_token`).

        Raises:
            EmailRequiredException: If the decrypted payload does not include an email.
            PasswordRequiredException: If the decrypted payload does not include a password.
            InvalidCredentialsException: If no matching user is found or the password is incorrect.
        """

        decrypted_data = await decrypt(
            rsa_key=request.app.state.rsa_key,
            enc_data=encrypted_data,
            encrypt_key=encrypted_key,
            iv_input=iv,
        )
        decrypted_data = json.loads(decrypted_data)

        email = decrypted_data.get("email")
        password = decrypted_data.get("password")

        if email is None:
            raise EmailRequiredException

        if password is None:
            raise PasswordRequiredException

        user = await self.session.scalar(
            select(UserModel).where(
                and_(UserModel.email == email, UserModel.role == RoleType.USER)
            )
        )
        if not user:
            raise InvalidCredentialsException
        verify = await verify_password(
            hashed_password=user.password, plain_password=password
        )
        if not verify:
            raise InvalidCredentialsException

        tokens = await create_tokens(user_id=user.id, role=user.role)

        return tokens

    #  MARK: - Create User
    # *======================================== Create User ========================================
    async def create_user(
        self, request: Request, encrypted_data: str, encrypted_key: str, iv: str
    ) -> SuccessResponse:
        """
        Create a new user account from RSA-encrypted payload and return a success message.

        Parameters:
            request (Request): FastAPI request object containing the application's RSA key at request.app.state.rsa_key.
            encrypted_data (str): RSA-encrypted JSON payload containing user fields (`name`, `username`, `country_code`, `phone`, `email`, `password`).
            encrypted_key (str): Encrypted symmetric key used to decrypt `encrypted_data`.
            iv (str): Initialization vector for symmetric decryption.

        Returns:
            SuccessResponse: Response containing a success message indicating the user was created.

        Raises:
            DuplicateEmailException: If a user with the provided email already exists.
            DuplicatePhoneException: If a user with the provided phone number already exists.
            DuplicateUsernameException: If a user with the provided username already exists.
            InvalidNameException, InvalidUserNameException, InvalidCountryCodeException, InvalidPhoneFormatException, InvalidEmailException, WeakPasswordException:
                If any of the corresponding input validations fail during field validation.
        """
        decrypted_data = await decrypt(
            rsa_key=request.app.state.rsa_key,
            enc_data=encrypted_data,
            encrypt_key=encrypted_key,
            iv_input=iv,
        )
        decrypted_data = json.loads(decrypted_data)

        name = decrypted_data.get("name")
        username = decrypted_data.get("username")
        country_code = decrypted_data.get("country_code")
        phone = decrypted_data.get("phone")
        email = decrypted_data.get("email")
        password = decrypted_data.get("password")

        self._validate_input_fields(
            name=name,
            username=username,
            country_code=country_code,
            phone=phone,
            email=email,
            password=password,
        )

        # Check for duplicate email, phone, or username
        existing_user = await self.session.scalar(
            select(UserModel)
            .options(load_only(UserModel.email, UserModel.username, UserModel.phone))
            .where(
                or_(
                    UserModel.email == email,
                    UserModel.phone == phone,
                    UserModel.username == username,
                )
            )
        )
        if existing_user:
            if existing_user.email == email:
                raise DuplicateEmailException
            if existing_user.phone == phone:
                raise DuplicatePhoneException
            if existing_user.username == username:
                raise DuplicateUsernameException

        user = UserModel.create(
            name=name,
            username=username,
            country_code=country_code,
            phone=phone,
            password=await hash_password(password),
            email=email,
            is_active=True,
            role=RoleType.USER,
        )
        self.session.add(user)

        return SuccessResponse(message=constants.USER_CREATED)

    #  MARK: - Validate Sign up Fields
    # *======================================== Validate Sign up Fields ========================================
    def _validate_input_fields(
        self,
        name: str,
        username: str,
        country_code: str,
        phone: str,
        email: str,
        password: str,
    ):
        """
        Validate user signup input fields and raise specific exceptions for any invalid value.

        Each argument is checked against the service's required format or policy and a
        corresponding exception is raised when validation fails.

        Raises:
            InvalidNameException: If `name` does not match the required name pattern.
            InvalidUserNameException: If `username` does not match the required username pattern.
            InvalidCountryCodeException: If `country_code` does not match the required country code pattern.
            InvalidPhoneFormatException: If `phone` does not match the required phone number format.
            InvalidEmailException: If `email` does not match the required email format.
            WeakPasswordException: If `password` does not satisfy the configured strength requirements.
        """

        if not re.search(NAME, name, re.I):
            raise InvalidNameException

        if not re.search(USERNAME, username, re.I):
            raise InvalidUserNameException

        if not re.search(COUNTRY_CODE, country_code, re.I):
            raise InvalidCountryCodeException

        if not re.match(PHONE_REGEX, phone, re.I):
            raise InvalidPhoneFormatException

        if not re.match(EMAIL_REGEX, email):
            raise InvalidEmailException

        if not strong_password(password):
            raise WeakPasswordException

    #  MARK: - Get User by ID
    # *======================================== Get User by ID ========================================
    async def get_user_by_id(self, user_id: UUID):
        """
        Retrieve a user by their ID.

        Args:
            user_id (UUID): The ID of the user to retrieve.

        Returns:
            UserModel: The user model with the requested user's information.
        """

        searched_user = await self.session.scalar(
            select(UserModel)
            .options(
                load_only(
                    UserModel.id,
                    UserModel.email,
                    UserModel.name,
                    UserModel.username,
                    UserModel.country_code,
                    UserModel.phone,
                    UserModel.is_active,
                    UserModel.role,
                )
            )
            .where(UserModel.id == user_id)
        )

        if not searched_user:
            raise UserNotFoundException
        return searched_user

    #  MARK: - Get Public Key
    # *======================================== Get Public Key ========================================
    async def get_public_key(self) -> PublicKeyResponse:
        """
        Retrieve the RSA public key for encryption.

        Returns:
            PublicKeyResponse: Object containing the public key in PEM format.

        Raises:
            FileNotFoundError: If the public key file is not found.
        """
        if not settings.PUBLIC_KEY_PATH:
            raise FileNotFoundError("Public key path is not configured")

        with open(settings.PUBLIC_KEY_PATH, "r") as key_file:
            public_key = key_file.read()

        return PublicKeyResponse(public_key=public_key)
