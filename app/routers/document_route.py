from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from app.dependencies import get_db
from app.controllers import document_controller
from app.schemas.document_schema import DocumentGet
from app.controllers.authentication import get_authentication_user


router = APIRouter(prefix="/document", tags=["document"])


@router.get("/{document_id}", response_model=DocumentGet)
async def get_document(
    document_id: int,
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a document by ID for the authenticated user."""
    return await document_controller.get_document(document_id, user, db)


@router.put("/{document_id}", response_model=DocumentGet)
async def update_document(
    document_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a document's file and metadata for the authenticated user."""
    return await document_controller.update_document(document_id, file, user, db)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    user: User = Depends(get_authentication_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document by ID for the authenticated user."""
    return await document_controller.delete_document(document_id, user, db)
