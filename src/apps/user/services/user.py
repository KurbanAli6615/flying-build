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
    InvalidCountryCodeException,
    InvalidCredentialsException,
    InvalidEmailException,
    InvalidNameException,
    InvalidPhoneFormatException,
    InvalidUserNameException,
    UserNotFoundException,
    WeakPasswordException,
)
from constants.regex import COUNTRY_CODE, EMAIL_REGEX, NAME, PHONE_REGEX, USERNAME
from core.common_helpers import create_tokens, decrypt
from core.utils.password import strong_password
from core.db import db_session
from core.exceptions import BadRequestError
from core.types import RoleType
from core.utils.hashing import hash_password, verify_password
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
    async def get_self(self, user_id: UUID) -> UserModel:
        """
        Retrieve user information by user ID.

        Args:
            user_id (UUID): The ID of the user.

        Returns:
            UserModel: The user model with the user's information.
        """
        return await self.session.scalar(
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

    #  MARK: - Login User
    # *======================================== Login User ========================================
    async def login_user(
        self, request: Request, encrypted_data: str, encrypted_key: str, iv: str
    ) -> dict[str, str]:
        """
         Log in a user and generate authentication tokens.

        Args:
             request: The FastAPI request object.
             encrypted_data (str): The encrypted data containing the login credentials.
             encrypted_key (str): The encrypted key used to encrypt the data.
             iv (str): The initialization vector used to encrypt the data.
         Returns:
             dict[str, str]: A dictionary containing the authentication tokens.

         Raises:
             InvalidCredentialsException: If the login credentials are invalid.
        """

        decrypted_data = await decrypt(
            rsa_key=request.app.state.rsa_key,
            enc_data=encrypted_data,
            encrypt_key=encrypted_key,
            iv_input=iv,
            time_check=True,
            timeout=constants.PAYLOAD_TIMEOUT,
        )
        decrypted_data = json.loads(decrypted_data)

        email = decrypted_data.get("email")
        password = decrypted_data.get("password")

        if email is None:
            raise BadRequestError(message=constants.EMAIL_FIELD_REQUIRED)

        if password is None:
            raise BadRequestError(message=constants.PASSWORD_FIELD_REQUIRED)

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

        return await create_tokens(user_id=user.id, role=user.role)

    #  MARK: - Create User
    # *======================================== Create User ========================================
    async def create_user(
        self, request: Request, encrypted_data: str, encrypted_key: str, iv: str
    ):
        """
        Create a new user.

        Args:
            email (EmailStr): The user's email address.
            password (str): The user's password.
            name (str): The user's name.
            username (str): The user's username.
            country_code (str): The user's country code.
            phone (str): The user's phone number.
            is_active (bool): The user's active status.
            role (RoleType): The user's role.

        Returns:
            UserModel: The created user model.

        Raises:
            DuplicateEmailException: If a user with the given email already exists.
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

        self.validate_input_fields(
            name=name,
            username=username,
            country_code=country_code,
            phone=phone,
            email=email,
            password=password,
        )

        user = await self.session.scalar(
            select(UserModel)
            .options(load_only(UserModel.email, UserModel.username))
            .where(or_(UserModel.email == email))
        )
        if user:
            raise DuplicateEmailException

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
        return user

    async def validate_input_fields(
        self,
        name: str,
        username: str,
        country_code: str,
        phone: str,
        email: str,
        password: str,
    ):
        """
        Validate the input fields of the user.

        Args:
            name (str): The user's  name.
            username (str): The user's username.
            country_code (str): The user's country code.
            phone (str): The user's phone number.
            email (str): The user's email address.
            password (str): The user's password.

        Raises:
            ValueError: If any of the fields are invalid.
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
