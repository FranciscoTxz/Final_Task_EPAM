from app.database import AsyncSessionLocal
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Return database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
