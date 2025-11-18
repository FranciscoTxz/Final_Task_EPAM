from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_project_model import UserProject
from app.schemas.user_project_schema import UserProjectCreate
from sqlalchemy.orm import selectinload


async def create_user_project(db: AsyncSession, user_project: UserProjectCreate):
    """Create a user-project relationship and persist it.

    Args:
        db: Async SQLAlchemy session used for database access.
        user_project: Payload with user_id, project_id, and ownership flag.

    Returns:
        db_user_project: The newly created UserProject instance.
    """
    db_user_project = UserProject(
        user_id=user_project.user_id,
        project_id=user_project.project_id,
        is_owner=user_project.is_owner,
    )
    db.add(db_user_project)
    await db.commit()
    await db.refresh(db_user_project)
    return db_user_project


async def get_user_projects(db: AsyncSession, user_id: int):
    """Retrieve all user-project relationships for a given user, including loaded Project objects.

    Args:
        db: Async SQLAlchemy session used for database access.
        user_id: ID of the user whose project memberships are requested.

    Returns:
        user_projects: The list of UserProject instances for the user.
    """
    result = await db.execute(
        select(UserProject)
        .options(selectinload(UserProject.project))
        .where(UserProject.user_id == user_id)
    )
    user_projects = result.scalars().all()
    return user_projects


async def is_project_from_user(db: AsyncSession, user_id: int, project_id: int):
    """Check whether a project belongs to a user and load the related Project.

    Args:
        db: Async SQLAlchemy session used for database access.
        user_id: ID of the user to verify membership.
        project_id: ID of the project to check.

    Returns:
        user_project: The matching UserProject instance if the user is a member; otherwise None.
    """
    result = await db.execute(
        select(UserProject)
        .options(selectinload(UserProject.project))
        .where(UserProject.user_id == user_id, UserProject.project_id == project_id)
    )
    return result.scalars().first()
