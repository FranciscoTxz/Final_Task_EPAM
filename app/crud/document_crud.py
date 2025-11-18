from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document_model import Document
from app.schemas.document_schema import DocumentUpdate


async def get_documents_by_project(db: AsyncSession, project_id: int):
    """Retrieve all documents belonging to a given project.

    Args:
        db: Async SQLAlchemy session used for database access.
        project_id: ID of the project whose documents are requested.

    Returns:
        documents: The list of Document instances for the specified project.
    """
    result = await db.execute(select(Document).where(Document.project_id == project_id))
    documents = result.scalars().all()
    return documents


async def get_document_by_id(db: AsyncSession, document_id: int):
    """Retrieve a single document by its ID.

    Args:
        db: Async SQLAlchemy session used for database access.
        document_id: ID of the document to fetch.

    Returns:
        document: The matching Document instance if found; otherwise None.
    """
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalars().first()


async def create_document(db: AsyncSession, project_id: int, name: str, url: str):
    """Create and persist a new document for a project.

    Args:
        db: Async SQLAlchemy session used for database access.
        project_id: ID of the project the document belongs to.
        name: Document name to store.
        url: Public URL pointing to the stored file.

    Returns:
        db_document: The newly created Document instance.
    """
    db_document = Document(project_id=project_id, name=name, url=url)
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    return db_document


async def update_document(db: AsyncSession, document_id: int, document: DocumentUpdate):
    """Update a document's name and/or URL if it exists.

    Args:
        db: Async SQLAlchemy session used for database access.
        document_id: ID of the document to update.
        document: Payload containing optional name and url updates.

    Returns:
        db_document: The updated Document instance if found; otherwise None.
    """
    db_document = await get_document_by_id(db, document_id)
    if not db_document:
        return None
    if document.name is not None:
        db_document.name = document.name
    if document.url is not None:
        db_document.url = document.url
    await db.commit()
    await db.refresh(db_document)
    return db_document


async def delete_document(db: AsyncSession, document_id: int):
    """Delete a document by its ID if it exists.

    Args:
        db: Async SQLAlchemy session used for database access.
        document_id: ID of the document to delete.

    Returns:
        True: Indicates the document was deleted successfully.
    """
    db_document = await get_document_by_id(db, document_id)
    if not db_document:
        return None
    await db.delete(db_document)
    await db.commit()
    return True
