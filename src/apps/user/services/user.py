import json
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

import constants
from apps.user.exceptions import (
    DuplicateEmailException,
    InvalidCredentialsException,
    UserNotFoundException,
)
from apps.user.models.user import UserModel
from core.common_helpers import create_tokens, decrypt, validate_input_fields
from core.db import db_session
from core.exceptions import BadRequestError
from core.types import RoleType
from core.utils.hashing import hash_password, verify_password


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
                    UserModel.first_name,
                    UserModel.last_name,
                )
            )
            .where(UserModel.id == user_id)
        )

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

    async def create_user(
        self, request: Request, encrypted_data: str, encrypted_key: str, iv: str
    ) -> UserModel:
        """
        Create a new user.

        Args:
            email (EmailStr): The user's email address.
            password (str): The user's password.
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            phone (str): The user's phone number.

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

        first_name = decrypted_data.get("first_name")
        last_name = decrypted_data.get("last_name")
        phone = decrypted_data.get("phone")
        email = decrypted_data.get("email")
        password = decrypted_data.get("password")

        validate_input_fields(
            first_name=first_name, email=email, phone=phone, password=password
        )

        user = await self.session.scalar(
            select(UserModel)
            .options(load_only(UserModel.email))
            .where(or_(UserModel.email == email, UserModel.phone == phone))
        )
        if user:
            raise DuplicateEmailException

        user = UserModel.create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=await hash_password(password),
            email=email,
        )
        self.session.add(user)
        return user

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
                    UserModel.first_name,
                    UserModel.last_name,
                )
            )
            .where(UserModel.id == user_id)
        )

        if not searched_user:
            raise UserNotFoundException
        return searched_user
