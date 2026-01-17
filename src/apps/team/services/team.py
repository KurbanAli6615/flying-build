from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import db_session
from fastapi import Depends
from fastapi import Request

from models import UserModel
from core.utils.schema import BaseResponse


class TeamService:
    def __init__(self, session: Annotated[AsyncSession, Depends(db_session)]):
        self.session = session

    #  MARK: - Create Team
    # *======================================== Create Team ========================================
    async def create_team(self, request: Request, user: UserModel) -> BaseResponse:
        pass
