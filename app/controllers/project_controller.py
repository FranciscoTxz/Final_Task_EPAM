from fastapi import HTTPException, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
)
from app.schemas.user_project_schema import UserProjectCreate
from app.crud.aws_crud import upload_file_to_s3
from app.crud import project_crud as crud_project
from app.crud import user_project_crud as crud_user_project
from app.crud import document_crud as crud_documents


async def get_project(user: User, db: AsyncSession):
    try:
        db_projects = await crud_user_project.get_user_projects(db, user.id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve projects: {str(e)}"
        )
    if not db_projects:
        raise HTTPException(status_code=404, detail="No projects found for the user")
    return db_projects


async def create_project(
    project: ProjectCreate,
    user: User,
    db: AsyncSession,
):
    if not project.name or not project.description:
        raise HTTPException(status_code=400, detail="Name and description are required")
    db_project = await crud_project.get_project_by_name(db, name=project.name)
    if db_project:
        raise HTTPException(status_code=400, detail="Project already exists")
    try:
        project_resp = await crud_project.create_project(db, project)
        await crud_user_project.create_user_project(
            db,
            UserProjectCreate(
                user_id=user.id, project_id=project_resp.id, is_owner=True
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create project: {str(e)}"
        )
    return {
        "message": f"Project created by {user.name}, Project Name: {project_resp.name}, ID: {project_resp.id}"
    }


async def get_project_info(project_id: int, user: User, db: AsyncSession):
    try:
        db_project = await crud_user_project.is_project_from_user(
            db, user.id, project_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve project: {str(e)}"
        )
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project.project


async def update_project(
    project_id: int, project: ProjectUpdate, user: User, db: AsyncSession
):
    try:
        db_user_project = await crud_user_project.is_project_from_user(
            db, user.id, project_id
        )
        if not db_user_project or not db_user_project.is_owner:
            raise HTTPException(status_code=404, detail="Project not found")
        updated_project = await crud_project.update_project(
            db, project_id, name=project.name, description=project.description
        )
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update project: {str(e)}"
        )
    return updated_project


async def delete_project(project_id: int, user: User, db: AsyncSession):
    try:
        db_user_project = await crud_user_project.is_project_from_user(
            db, user.id, project_id
        )
        if not db_user_project or not db_user_project.is_owner:
            raise HTTPException(status_code=404, detail="Project not found")
        deleted_project = await crud_project.delete_project(db, project_id)
        if not deleted_project:
            raise HTTPException(status_code=404, detail="Project not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete project: {str(e)}"
        )
    return {"message": f"Project with ID {deleted_project.id} deleted successfully"}


async def get_project_documents(project_id: int, user: User, db: AsyncSession):
    try:
        db_user_project = await crud_user_project.is_project_from_user(
            db, user.id, project_id
        )
        if not db_user_project:
            raise HTTPException(status_code=404, detail="Project not found")
        documents = await crud_documents.get_documents_by_project(db, project_id)
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found for project")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve documents: {str(e)}"
        )
    return documents


async def create_project_document(project_id: int, file: File, user: User, db: AsyncSession):
    try:
        db_user_project = await crud_user_project.is_project_from_user(
            db, user.id, project_id
        )
        if not db_user_project:
            raise HTTPException(status_code=404, detail="Project not found")

        url = await upload_file_to_s3(file)

        new_document = await crud_documents.create_document(
            db, project_id, file.filename, url
        )
        if not new_document:
            raise HTTPException(status_code=500, detail="Failed to create document")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create document: {str(e)}"
        )
    return new_document


async def invite_user_to_project(project_id: int, user_id: int, user: User, db: AsyncSession):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required to invite")
        db_user_project = await crud_user_project.is_project_from_user(
            db, user.id, project_id
        )
        if not db_user_project or not db_user_project.is_owner:
            raise HTTPException(status_code=404, detail="Project not found")
        db_user_invited_project = await crud_user_project.is_project_from_user(
            db, user_id, project_id
        )
        if db_user_invited_project:
            raise HTTPException(
                status_code=400, detail="User is already a member of the project"
            )
        await crud_user_project.create_user_project(
            db,
            user_project=UserProjectCreate(
                user_id=user_id, project_id=project_id, is_owner=False
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to invite user: {str(e)}")
    return {
        "message": f"User with ID {user_id} invited to project {project_id} successfully"
    }
