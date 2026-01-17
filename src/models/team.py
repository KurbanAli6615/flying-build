from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.utils.mixins import TimeStampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.join_request import JoinRequestModel
    from models.team_member import TeamMemberModel


class TeamModel(Base, UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Model for representing a team.

    Attributes:
        owner_id (UUID): The ID of the user who owns the team.
        name (str): The name of the team.
        description (str | None): The description of the team.
        team_code (str): Unique code for joining the team.
        is_active (bool): Whether the team is active.
    """

    __tablename__ = "teams"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    team_code: Mapped[str] = mapped_column(index=True, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    members: Mapped[list["TeamMemberModel"]] = relationship(
        "TeamMemberModel", back_populates="team", lazy="selectin"
    )
    join_requests: Mapped[list["JoinRequestModel"]] = relationship(
        "JoinRequestModel", back_populates="team", lazy="selectin"
    )
