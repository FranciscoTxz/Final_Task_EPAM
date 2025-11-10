from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project_model import Project
from app.schemas.project_schema import ProjectCreate


async def get_project_by_name(db: AsyncSession, name: str):
    """Retrieve a project by its unique name.

    Args:
        db: Async SQLAlchemy session used for database access.
        name: Unique project name to search for.

    Returns:
        project: The matching Project instance if found; otherwise None.
    """
    result = await db.execute(select(Project).where(Project.name == name))
    return result.scalars().first()


async def create_project(db: AsyncSession, project: ProjectCreate):
    """Create and persist a new project.

    Args:
        db: Async SQLAlchemy session used for database access.
        project: Payload containing the project's name and description.

    Returns:
        db_project: The newly created Project instance.
    """
    db_project = Project(name=project.name, description=project.description)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


async def update_project(
    db: AsyncSession,
    project_id: int,
    name: str | None = None,
    description: str | None = None,
):
    """Update a project's name and/or description.

    Args:
        db: Async SQLAlchemy session used for database access.
        project_id: ID of the project to update.
        name: Optional new project name.
        description: Optional new project description.

    Returns:
        db_project: The updated Project instance if found; otherwise None.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    db_project = result.scalars().first()
    if not db_project:
        return None
    if name:
        db_project.name = name
    if description:
        db_project.description = description
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


async def delete_project(db: AsyncSession, project_id: int):
    """Delete a project by its ID.

    Args:
        db: Async SQLAlchemy session used for database access.
        project_id: ID of the project to delete.

    Returns:
        db_project: The deleted Project instance if found; otherwise None.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    db_project = result.scalars().first()
    if not db_project:
        return None
    await db.delete(db_project)
    await db.commit()
    return db_project
