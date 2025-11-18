from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from app.schemas.user_schema import UserCreate


async def get_user_by_name(db: AsyncSession, name: str):
    """Retrieve a user by their unique name.

    Args:
        db: Async SQLAlchemy session used for database access.
        name: Username to search for.

    Returns:
        user: The matching User instance if found; otherwise None.
    """
    result = await db.execute(select(User).where(User.name == name))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate):
    """Create and persist a new user.

    Args:
        db: Async SQLAlchemy session used for database access.
        user: Payload containing the user's name and (already hashed) password.

    Returns:
        db_user: The newly created User instance.
    """
    db_user = User(name=user.name, password=user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
