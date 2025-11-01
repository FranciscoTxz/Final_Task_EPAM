from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_project_model import UserProject
from app.schemas.user_project_schema import UserProjectCreate
from sqlalchemy.orm import selectinload


async def create_user_project(db: AsyncSession, user_project: UserProjectCreate):
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
    result = await db.execute(
        select(UserProject)
        .options(selectinload(UserProject.project))
        .where(UserProject.user_id == user_id)
    )
    user_projects = result.scalars().all()
    return user_projects


async def is_project_from_user(db: AsyncSession, user_id: int, project_id: int):
    result = await db.execute(
        select(UserProject)
        .options(selectinload(UserProject.project))
        .where(UserProject.user_id == user_id, UserProject.project_id == project_id)
    )
    return result.scalars().first()
