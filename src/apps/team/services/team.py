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
        Create a TeamService bound to a database session.
        
        Parameters:
            session (AsyncSession): Database session injected via FastAPI Depends(db_session) used for database operations.
        """
        self.session = session

    #  MARK: - Create Team
    # *======================================== Create Team ========================================
    async def create_team(self, request: Request, user: UserModel) -> BaseResponse:
        """
        Create a new team using data from the request on behalf of the given user.
        
        Parameters:
            request (Request): HTTP request containing the team creation payload.
            user (UserModel): User performing the action; used for ownership and authorization context.
        
        Returns:
            BaseResponse: Result of the creation operation containing status and any data or error information.
        """
        pass