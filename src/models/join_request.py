from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.types import JoinRequestStatus
from core.utils.mixins import TimeStampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.team import TeamModel
    from models.user import UserModel


class JoinRequestModel(Base, UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Model for representing team join requests.

    This model tracks requests from users to join teams, including the status
    of the request and who reviewed it.

    Attributes:
        team_id (UUID): The ID of the team.
        requested_by (UUID): The ID of the user requesting to join.
        status (JoinRequestStatus): The status of the request.
        reviewed_by (UUID | None): The ID of the user who reviewed the request.
        reviewed_at (datetime | None): The timestamp when the request was reviewed.
    """

    __tablename__ = "join_requests"
    # Note: A partial unique index is enforced at the database level via migration
    # (uq_join_request_team_user_pending) that only applies to PENDING status.
    # This allows historical duplicates (APPROVED/DECLINED) but prevents concurrent PENDING requests.

    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id"), index=True)
    requested_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[JoinRequestStatus] = mapped_column(
        default=JoinRequestStatus.PENDING, index=True
    )
    reviewed_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    team: Mapped["TeamModel"] = relationship(
        "TeamModel", back_populates="join_requests"
    )
    requester: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[requested_by]
    )
    reviewer: Mapped["UserModel | None"] = relationship(
        "UserModel", foreign_keys=[reviewed_by]
    )
