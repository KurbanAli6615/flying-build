import uuid
from typing import Self

from sqlalchemy.orm import Mapped, mapped_column

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
    first_name: Mapped[str] = mapped_column(index=True)
    last_name: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    phone: Mapped[str] = mapped_column(index=True, unique=True)
    password: Mapped[str] = mapped_column()
    role: Mapped[RoleType] = mapped_column()

    def __str__(self) -> str:
        """
        Return a string representation of the user.

        :return: A string with the user's first and last name.
        """
        return f"<{self.first_name} {self.last_name}>"

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
        password: str,
        role: str = RoleType.USER,
    ) -> Self:
        """
        Create a new user.

        :param first_name: The user's first name.
        :param last_name: The user's last name.
        :param phone: The user's phone number.
        :param email: The user's email address.
        :param password: The user's hashed password.
        :param role: The user's role identifier. Defaults to RoleType.USER.
        :return: An instance of UserModel.
        """
        return cls(
            id=uuid.uuid4(),
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            phone=phone,
            password=password,
            role=role,
        )
