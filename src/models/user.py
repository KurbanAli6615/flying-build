import uuid
from typing import Self

from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.types import RoleType
from core.utils.mixins import TimeStampMixin, UUIDPrimaryKeyMixin


class UserModel(Base, UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Model for representing user information.

    This SQLAlchemy model represents user information, including fields such as first_name, last_name, email, phone,
    password, and role. It is used to store and manage user data in the application's database.

    Attributes:
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        email (str): The user's email address (unique).
        phone (str): The user's phone number (unique).
        password (str): The user's hashed password.
        role (int): The user's role identifier.
    """

    __tablename__ = "users"
    name: Mapped[str] = mapped_column(index=True)
    username: Mapped[str] = mapped_column(index=True, unique=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    country_code: Mapped[str] = mapped_column(index=True)
    phone: Mapped[str] = mapped_column(index=True, unique=True)
    password: Mapped[str] = mapped_column()
    role: Mapped[RoleType] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    # ⭐ One-to-Many → teams created by the user
    owned_teams = relationship("TeamModel")

    def __str__(self) -> str:
        """
        Return a string representation of the user.

        :return: A string with the user's first and last name.
        """
        return f"<{self.name} {self.username}>"

    @classmethod
    def create(
        cls,
        name: str,
        username: str,
        country_code: str,
        phone: str,
        email: str,
        password: str,
        is_active: bool = True,
        role: str = RoleType.USER,
    ) -> Self:
        """
        Create a new user.

        :param name: The user's name.
        :param username: The user's username.
        :param country_code: The user's country code.
        :param phone: The user's phone number.
        :param email: The user's email address.
        :param password: The user's hashed password.
        :param is_active: The user's active status. Defaults to True.
        :param role: The user's role identifier. Defaults to RoleType.USER.
        :return: An instance of UserModel.
        """
        return cls(
            id=uuid.uuid4(),
            name=name,
            username=username,
            country_code=country_code,
            email=email.lower(),
            phone=phone,
            password=password,
            role=role,
            is_active=is_active,
        )
