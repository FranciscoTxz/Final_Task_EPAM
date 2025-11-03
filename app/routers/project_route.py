from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from app.dependencies import get_db
from app.schemas.project_schema import (
    ProjectCreate,
    SuccessResponse,
    ProjectInfo,
    ProjectUpdate,
)
from app.schemas.user_project_schema import UserProjectWithProject
from app.schemas.document_schema import DocumentProjectInfo
from app.controllers.authentication import get_authentication_user
from app.controllers import project_controller


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[UserProjectWithProject])
async def get_projects(
    user: User = Depends(get_authentication_user), db: AsyncSession = Depends(get_db)
):
    return await project_controller.get_project(user, db)


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_controller.create_project(project, user, db)


router_project = APIRouter(prefix="/project", tags=["project"])


@router_project.get("/{project_id}/info", response_model=ProjectInfo)
async def get_project_info(
    project_id: int,
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_controller.get_project_info(project_id, user, db)


@router_project.put("/{project_id}/info", response_model=ProjectCreate)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_controller.update_project(project_id, project, user, db)


@router_project.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_controller.delete_project(project_id, user, db)


@router_project.get("/{project_id}/documents", response_model=list[DocumentProjectInfo])
async def get_project_documents(
    project_id: int,
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_controller.get_project_documents(project_id, user, db)


@router_project.post(
    "/{project_id}/documents", status_code=201, response_model=DocumentProjectInfo
)
async def create_project_document(
    project_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_controller.create_project_document(project_id, file, user, db)


@router_project.post(
    "/{project_id}/invite", status_code=200, response_model=SuccessResponse
)
async def invite_user_to_project(
    project_id: int,
    user_id: int,
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    return await project_controller.invite_user_to_project(project_id, user_id, user, db)
