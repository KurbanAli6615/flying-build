from core.db import async_session
from core.utils import logger


async def job() -> None:
    """
    Perform a cron job.

    This function is executed as a cron job. It may perform various tasks, including but not limited to checking
    subscription status.

    Returns:
        None: This function does not return any meaningful value upon completion.
    """
    logger.info("Running cron job!")
    async with async_session() as session:
        async with session.begin():
            await session.execute()
    logger.info("Finished cron job!")
    return None
