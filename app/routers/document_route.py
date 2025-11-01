from fastapi import Depends, APIRouter, UploadFile, File
from pytest import Session
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
    db: Session = Depends(get_db),
):
    return await document_controller.get_document(document_id, user, db)


@router.put("/{document_id}", response_model=DocumentGet)
async def update_document(
    document_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_authentication_user),
    db: Session = Depends(get_db),
):
    return await document_controller.update_document(document_id, file, user, db)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    user: User = Depends(get_authentication_user),
    db: Session = Depends(get_db),
):
    return await document_controller.delete_document(document_id, user, db)
