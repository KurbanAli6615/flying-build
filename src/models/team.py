from core.db import Base
from core.utils.mixins import TimeStampMixin, UUIDPrimaryKeyMixin
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from sqlalchemy import ForeignKey


class TeamModel(Base, UUIDPrimaryKeyMixin, TimeStampMixin):
    __tablename__ = "teams"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    team_code: Mapped[str] = mapped_column(index=True, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
