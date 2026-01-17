from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.types import TeamRole
from core.utils.mixins import TimeStampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.team import TeamModel
    from models.user import UserModel


class TeamMemberModel(Base, UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Model for representing team membership.

    This model represents the many-to-many relationship between users and teams,
    including the role each user has within a team.

    Attributes:
        team_id (UUID): The ID of the team.
        user_id (UUID): The ID of the user.
        role (TeamRole): The role of the user in the team.
    """

    __tablename__ = "team_members"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_members_team_user"),
    )

    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[TeamRole] = mapped_column(index=True)

    team: Mapped["TeamModel"] = relationship("TeamModel", back_populates="members")
    user: Mapped["UserModel"] = relationship("UserModel")
