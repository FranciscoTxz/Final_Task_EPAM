from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document_model import Document
from app.schemas.document_schema import DocumentUpdate


async def get_documents_by_project(db: AsyncSession, project_id: int):
    result = await db.execute(select(Document).where(Document.project_id == project_id))
    documents = result.scalars().all()
    # Each Document instance will have the related User loaded as .user
    return documents


async def get_document_by_id(db: AsyncSession, document_id: int):
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalars().first()


async def create_document(db: AsyncSession, project_id: int, name: str, url: str):
    db_document = Document(project_id=project_id, name=name, url=url)
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    return db_document


async def update_document(db: AsyncSession, document_id: int, document: DocumentUpdate):
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
    db_document = await get_document_by_id(db, document_id)
    if not db_document:
        return None
    await db.delete(db_document)
    await db.commit()
    return True
