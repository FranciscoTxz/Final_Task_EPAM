from fastapi import HTTPException, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from app.crud import document_crud as crud_document
from app.crud import user_project_crud as crud_user_project
from app.schemas.document_schema import DocumentUpdate
from app.crud.aws_crud import delete_file_from_s3, upload_file_to_s3


async def get_document(
    document_id: int,
    user: User,
    db: AsyncSession,
):
    """Return the document instance if it exists and belongs to a project the user is a member of.

    Args:
        document_id: ID of the document to retrieve.
        user: Authenticated user requesting the document.
        db: Async SQLAlchemy session used for database access.

    Returns:
        db_document: The document instance if it exists and belongs to a project the user is a member of.

    Raises:
        HTTPException: 404 if the document does not exist or does not belong to the user; 500 on unexpected errors.
    """
    try:
        db_document = await crud_document.get_document_by_id(db, document_id)
        if not db_document:
            raise HTTPException(status_code=404, detail="Document not found")
        db_user_project = await crud_user_project.is_project_from_user(
            db, user.id, db_document.project_id
        )
        if not db_user_project:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve document: {str(e)}"
        )
    return db_document


async def update_document(
    document_id: int,
    file: File,
    user: User,
    db: AsyncSession,
):
    """Return the updated document after replacing its stored file and metadata.

    Args:
        document_id: ID of the document to update.
        file: Uploaded file used to replace the existing document content.
        user: Authenticated user requesting the update.
        db: Async SQLAlchemy session used for database access.

    Returns:
        db_document: The updated document instance with new name and URL.

    Raises:
        HTTPException: 404 if the document does not exist or does not belong to the user; 500 on unexpected errors.
    """
    try:
        db_document = await crud_document.get_document_by_id(db, document_id)
        if not db_document:
            raise HTTPException(status_code=404, detail="Document not found")
        db_user_project = await crud_user_project.is_project_from_user(
            db, user.id, db_document.project_id
        )
        if not db_user_project:
            raise HTTPException(status_code=404, detail="Document not found")
        await delete_file_from_s3(db_document.url)
        url = await upload_file_to_s3(file)
        document = DocumentUpdate(name=file.filename, url=url)
        db_document = await crud_document.update_document(db, document_id, document)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update document: {str(e)}"
        )
    return db_document


async def delete_document(
    document_id: int,
    user: User,
    db: AsyncSession,
):
    """Delete a document and its associated file from storage.

    Args:
        document_id: ID of the document to delete.
        user: Authenticated user requesting the deletion.
        db: Async SQLAlchemy session used for database access.

    Returns:
        None: The operation completes without returning a value.

    Raises:
        HTTPException: 404 if the document does not exist or does not belong to the user; 500 on unexpected errors.
    """
    try:
        db_document = await crud_document.get_document_by_id(db, document_id)
        if not db_document:
            raise HTTPException(status_code=404, detail="Document not found")
        db_user_project = await crud_user_project.is_project_from_user(
            db, user.id, db_document.project_id
        )
        if not db_user_project:
            raise HTTPException(status_code=404, detail="Document not found")
        await delete_file_from_s3(db_document.url)
        await crud_document.delete_document(db, document_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete document: {str(e)}"
        )
    return
