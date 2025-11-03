import asyncio
import pytest
from fastapi import HTTPException
from app.routers.document_route import get_document, update_document, delete_document
from app.crud import user_project_crud as crud_user_project
from app.crud import document_crud as crud_documents
from tests.test_project import DummyUserProject, DummyProject
from tests.test_users import DummyUser
import app.controllers.document_controller as controller
from tests.test_project import DummyUploadFile


class DummyDocument:
    def __init__(self, id: int, name: str, url: str, project_id: int):
        self.id = id
        self.name = name
        self.url = url
        self.project_id = project_id


class DummyDocumentUpdate:
    def __init__(self, name: str = None, url: str = None):
        self.name = name
        self.url = url


def test_get_document_success(monkeypatch):
    """Get document for a user: returns the document"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return DummyUserProject(
            is_owner=True,
            project=DummyProject(id=1, name="Project1", description="Desc"),
        )

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    result = asyncio.run(
        get_document(
            document_id=document_id,
            user=DummyUser(id=1, name="alice", password="secret"),
            db=None,
        )
    )

    assert isinstance(result, DummyDocument)
    assert result.id == document_id
    assert result.name == "Doc1"
    assert result.url == "http://example.com/doc1"
    assert result.project_id == 1


def test_get_document_not_found(monkeypatch):
    """Get document: document not found -> 404"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return None

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Document not found"


def test_get_document_not_project_from_user(monkeypatch):
    """Get document: project not associated with user -> 404"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return None

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Document not found"


def test_get_document_search_exception(monkeypatch):
    """Get document DB error when fetching -> 500"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        raise Exception("Database error")

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to retrieve document:" in excinfo.value.detail


def test_get_document_project_from_user_exception(monkeypatch):
    """Get document DB error when checking project -> 500"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        raise Exception("Database error")

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to retrieve document:" in excinfo.value.detail


def test_update_document_success(monkeypatch):
    """Update document for a user: returns updated document"""
    document_id = 1
    file = DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return DummyUserProject(
            is_owner=True,
            project=DummyProject(id=1, name="Project1", description="Desc"),
        )

    async def fake_upload_file_to_s3(file):
        return "https://bucket.s3.amazonaws.com/mydoc.txt"

    async def fake_delete_file_from_s3(url):
        return True

    async def fake_update_document(db, document_id: int, document: DummyDocumentUpdate):
        return DummyDocument(
            id=document_id,
            name=document.name,
            url=document.url,
            project_id=1
        )

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(controller, "delete_file_from_s3", fake_delete_file_from_s3)
    monkeypatch.setattr(
        controller, "upload_file_to_s3", fake_upload_file_to_s3
    )
    monkeypatch.setattr(crud_documents, "update_document", fake_update_document)

    result = asyncio.run(
        update_document(
            document_id=document_id,
            file=file,
            user=DummyUser(id=1, name="alice", password="secret"),
            db=None,
        )
    )

    assert isinstance(result, DummyDocument)
    assert result.id == document_id
    assert result.name == "mydoc.txt"
    assert result.url == "https://bucket.s3.amazonaws.com/mydoc.txt"
    assert result.project_id == 1


def test_update_document_not_found(monkeypatch):
    """Update document: document not found -> 404"""
    document_id = 1
    file = DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_get_document_by_id(db, document_id: int):
        return None

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_document(
                document_id=document_id,
                file=file,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 404
    assert "Document not found" == excinfo.value.detail


def test_update_document_not_project_user(monkeypatch):
    """Update document: project not associated with user -> 404"""
    document_id = 1
    file = DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return None

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_document(
                document_id=document_id,
                file=file,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 404
    assert "Document not found" == excinfo.value.detail


def test_update_document_get_document_exception(monkeypatch):
    """Update document DB error when fetching -> 500"""
    document_id = 1
    file = DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_get_document_by_id(db, document_id: int):
        raise Exception("Database error")

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_document(
                document_id=document_id,
                file=file,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to update document:" in excinfo.value.detail


def test_update_document_is_project_from_user_exception(monkeypatch):
    """Update document DB error when checking project -> 500"""
    document_id = 1
    file = DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        raise Exception("Database error")

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_document(
                document_id=document_id,
                file=file,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to update document:" in excinfo.value.detail


def test_update_document_update_document_exception(monkeypatch):
    """Update document DB error when updating -> 500"""
    document_id = 1
    file = DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return DummyUserProject(
            is_owner=True,
            project=DummyProject(id=1, name="Project1", description="Desc"),
        )

    async def fake_update_document(db, document_id: int, document: DummyDocumentUpdate):
        raise Exception("Database error")

    async def fake_upload_file_to_s3(file):
        return "https://bucket.s3.amazonaws.com/mydoc.txt"

    async def fake_delete_file_from_s3(url):
        return True

    monkeypatch.setattr(controller, "delete_file_from_s3", fake_delete_file_from_s3)
    monkeypatch.setattr(
        controller, "upload_file_to_s3", fake_upload_file_to_s3
    )
    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_documents, "update_document", fake_update_document)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_document(
                document_id=document_id,
                file=file,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to update document:" in excinfo.value.detail


def test_update_document_exception_upload_aws(monkeypatch):
    """Update document AWS upload error -> 500"""
    document_id = 1
    file = DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return DummyUserProject(
            is_owner=True,
            project=DummyProject(id=1, name="Project1", description="Desc"),
        )

    async def fake_upload_file_to_s3(file):
        raise Exception("DB Error")

    async def fake_delete_file_from_s3(url):
        return True

    async def fake_update_document(db, document_id: int, document: DummyDocumentUpdate):
        return DummyDocument(
            id=document_id,
            name=document.name,
            url=document.url,
            project_id=1
        )

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(controller, "delete_file_from_s3", fake_delete_file_from_s3)
    monkeypatch.setattr(
        controller, "upload_file_to_s3", fake_upload_file_to_s3
    )
    monkeypatch.setattr(crud_documents, "update_document", fake_update_document)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_document(
                document_id=document_id,
                file=file,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to update document:" in excinfo.value.detail


def test_update_document_exception_delete_aws(monkeypatch):
    """Update document AWS delete error -> 500"""
    document_id = 1
    file = DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return DummyUserProject(
            is_owner=True,
            project=DummyProject(id=1, name="Project1", description="Desc"),
        )

    async def fake_upload_file_to_s3(file):
        return "https:..."

    async def fake_delete_file_from_s3(url):
        raise Exception("DB Error")

    async def fake_update_document(db, document_id: int, document: DummyDocumentUpdate):
        return DummyDocument(
            id=document_id,
            name=document.name,
            url=document.url,
            project_id=1
        )

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(controller, "delete_file_from_s3", fake_delete_file_from_s3)
    monkeypatch.setattr(
        controller, "upload_file_to_s3", fake_upload_file_to_s3
    )
    monkeypatch.setattr(crud_documents, "update_document", fake_update_document)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_document(
                document_id=document_id,
                file=file,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to update document:" in excinfo.value.detail


def test_delete_document_success(monkeypatch):
    """Delete document for a user: OK"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return DummyUserProject(
            is_owner=True,
            project=DummyProject(id=1, name="Project1", description="Desc"),
        )

    async def fake_delete_file_from_s3(url):
        return True

    async def fake_delete_document(db, document_id: int):
        return True

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(controller, "delete_file_from_s3", fake_delete_file_from_s3)
    monkeypatch.setattr(crud_documents, "delete_document", fake_delete_document)

    result = asyncio.run(
        delete_document(
            document_id=document_id,
            user=DummyUser(id=1, name="alice", password="secret"),
            db=None,
        )
    )

    assert result is None


def test_delete_document_not_found(monkeypatch):
    """Delete document: document not found -> 404"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return None

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 404
    assert "Document not found" == excinfo.value.detail


def test_delete_document_not_project_user(monkeypatch):
    """Delete document: project not associated with user -> 404"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return None

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 404
    assert "Document not found" == excinfo.value.detail


def test_delete_document_get_document_exception(monkeypatch):
    """Delete document DB error when fetching -> 500"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        raise Exception("Database error")

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to delete document:" in excinfo.value.detail


def test_delete_document_is_project_from_user_exception(monkeypatch):
    """Delete document DB error when checking project -> 500"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        raise Exception("Database error")

    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to delete document:" in excinfo.value.detail


def test_delete_document_delete_document_exception(monkeypatch):
    """Delete document DB error when deleting -> 500"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return DummyUserProject(
            is_owner=True,
            project=DummyProject(id=1, name="Project1", description="Desc"),
        )

    async def fake_delete_document(db, document_id: int):
        raise Exception("Database error")

    async def fake_delete_file_from_s3(url):
        raise Exception("DB Error")

    monkeypatch.setattr(controller, "delete_file_from_s3", fake_delete_file_from_s3)
    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_documents, "delete_document", fake_delete_document)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to delete document:" in excinfo.value.detail


def test_delete_document_delete_document_aws_exception(monkeypatch):
    """Delete document AWS delete error -> 500"""
    document_id = 1

    async def fake_get_document_by_id(db, document_id: int):
        return DummyDocument(
            id=document_id, name="Doc1", url="http://example.com/doc1", project_id=1
        )

    async def fake_is_project_from_user(db, user_id: int, document_id: int):
        return DummyUserProject(
            is_owner=True,
            project=DummyProject(id=1, name="Project1", description="Desc"),
        )

    async def fake_delete_document(db, document_id: int):
        return True

    async def fake_delete_file_from_s3(url):
        raise Exception("DB Error")

    monkeypatch.setattr(controller, "delete_file_from_s3", fake_delete_file_from_s3)
    monkeypatch.setattr(crud_documents, "get_document_by_id", fake_get_document_by_id)
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_documents, "delete_document", fake_delete_document)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_document(
                document_id=document_id,
                user=DummyUser(id=1, name="alice", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500
    assert "Failed to delete document:" in excinfo.value.detail
