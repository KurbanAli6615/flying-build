from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import db_session
from core.utils.schema import BaseResponse
from models import UserModel


class TeamService:
    """
    Service with methods to handle team creation.
    """

    def __init__(self, session: Annotated[AsyncSession, Depends(db_session)]):
        """
        Initialize TeamService with a database session.
        """
        self.session = session

    #  MARK: - Create Team
    # *======================================== Create Team ========================================
    async def create_team(self, request: Request, user: UserModel) -> BaseResponse:
        """
        Create a new team.

        Args:
            request: The request object.
            user: The user object.

        Returns:
            BaseResponse: The response object.
        """
        pass
