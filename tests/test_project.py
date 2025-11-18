import asyncio
import pytest
from fastapi import HTTPException
from app.routers.project_route import (
    create_project,
    delete_project,
    update_project,
    get_project_info,
    get_projects,
    get_project_documents,
    create_project_document,
    invite_user_to_project,
)
from app.crud import user_project_crud as crud_user_project
from app.crud import project_crud as crud_project
from app.crud import document_crud as crud_documents
import app.controllers.project_controller as controller
import tests.dummies as dummies


def test_get_projects_success(monkeypatch):
    """Get projects for a user: returns the list of projects"""
    test_user_id = 1

    async def fake_get_user_projects(db, user_id: int):
        return [
            dummies.DummyUserProject(
                is_owner=True,
                project=dummies.DummyProject(id=1, name="Project1", description="Desc1"),
            ),
            dummies.DummyUserProject(
                is_owner=False,
                project=dummies.DummyProject(id=2, name="Project2", description="Desc2"),
            ),
        ]

    monkeypatch.setattr(crud_user_project, "get_user_projects", fake_get_user_projects)

    result = asyncio.run(
        get_projects(
            user=dummies.DummyUser(id=test_user_id, name="alice", password="secret"), db=None
        )
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].is_owner is True
    assert result[0].project.name == "Project1"
    assert result[1].is_owner is False
    assert result[1].project.name == "Project2"


def test_get_projects_empty(monkeypatch):
    """Get projects for a user with no projects: returns empty list"""
    test_user_id = 2

    async def fake_get_user_projects(db, user_id: int):
        return []

    monkeypatch.setattr(crud_user_project, "get_user_projects", fake_get_user_projects)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_projects(
                user=dummies.DummyUser(id=test_user_id, name="bob", password="secret"), db=None
            )
        )

    assert excinfo.value.status_code == 404


def test_get_projects_exception(monkeypatch):
    """Get projects raises exception: raises HTTPException 500"""
    test_user_id = 3

    async def fake_get_user_projects(db, user_id: int):
        raise Exception("DB error")

    monkeypatch.setattr(crud_user_project, "get_user_projects", fake_get_user_projects)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_projects(
                user=dummies.DummyUser(id=test_user_id, name="charlie", password="secret"),
                db=None,
            )
        )

    assert excinfo.value.status_code == 500


def test_post_projects_success(monkeypatch):
    """Create a new project for a user: returns the created project"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")

    async def fake_get_project_by_name(db, name: str):
        return []

    async def fake_create_project(db, project: dummies.DummyCreateProject):
        return dummies.DummyProject(id=3, name=project.name, description=project.description)

    async def fake_create_user_project(db, user_project: dummies.DummyUserProjectCreate):
        return

    monkeypatch.setattr(crud_project, "get_project_by_name", fake_get_project_by_name)
    monkeypatch.setattr(crud_project, "create_project", fake_create_project)
    monkeypatch.setattr(
        crud_user_project, "create_user_project", fake_create_user_project
    )

    project = dummies.DummyCreateProject(name="NewProject", description="NewDesc")

    result = asyncio.run(create_project(project=project, user=user, db=None))

    assert isinstance(result, dict)
    assert (
        result.get("message")
        == f"Project created by {user.name}, Project Name: {project.name}, ID: {3}"
    )


def test_post_projects_no_name(monkeypatch):
    """Create a new project for a user: missing name -> 400"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")

    project = dummies.DummyCreateProject(name="", description="NewDesc")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(create_project(project=project, user=user, db=None))

    assert excinfo.value.status_code == 400


def test_post_projects_project_exists(monkeypatch):
    """Create a new project for a user: project exists -> 400"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")

    async def fake_get_project_by_name(db, name: str):
        return [dummies.DummyProject(id=1, name=name, description="ExistingDesc")]

    monkeypatch.setattr(crud_project, "get_project_by_name", fake_get_project_by_name)

    project = dummies.DummyCreateProject(name="NewProject", description="NewDesc")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(create_project(project=project, user=user, db=None))

    assert excinfo.value.status_code == 400


def test_post_projects_exception_create_project(monkeypatch):
    """Create a new project for a user: DB error creating project -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")

    async def fake_get_project_by_name(db, name: str):
        return []

    async def fake_create_project(db, project: dummies.DummyCreateProject):
        raise Exception("DB error")

    monkeypatch.setattr(crud_project, "get_project_by_name", fake_get_project_by_name)
    monkeypatch.setattr(crud_project, "create_project", fake_create_project)

    project = dummies.DummyCreateProject(name="NewProject", description="NewDesc")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(create_project(project=project, user=user, db=None))

    assert excinfo.value.status_code == 500


def test_post_projects_exception_create_user_project(monkeypatch):
    """Create a new project for a user: DB error creating user_project -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")

    async def fake_get_project_by_name(db, name: str):
        return []

    async def fake_create_project(db, project: dummies.DummyCreateProject):
        return dummies.DummyProject(id=3, name=project.name, description=project.description)

    async def fake_create_user_project(db, user_project: dummies.DummyUserProjectCreate):
        raise Exception("DB error")

    monkeypatch.setattr(crud_project, "get_project_by_name", fake_get_project_by_name)
    monkeypatch.setattr(crud_project, "create_project", fake_create_project)
    monkeypatch.setattr(
        crud_user_project, "create_user_project", fake_create_user_project
    )

    project = dummies.DummyCreateProject(name="NewProject", description="NewDesc")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(create_project(project=project, user=user, db=None))

    assert excinfo.value.status_code == 500


def test_get_project_info_success(monkeypatch):
    """Get project info for a user's project: returns project info"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=True,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    result = asyncio.run(get_project_info(project_id=project_id, user=user, db=None))

    assert isinstance(result, dummies.DummyProject)
    assert result.id == project_id
    assert result.name == "Project1"


def test_get_project_info_no_project(monkeypatch):
    """Get project info when project not found: 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return []

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(get_project_info(project_id=project_id, user=user, db=None))

    assert excinfo.value.status_code == 404


def test_get_project_info_exception_is_project_from_user(monkeypatch):
    """Get project info raises exception: HTTPException 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(get_project_info(project_id=project_id, user=user, db=None))

    assert excinfo.value.status_code == 500


def test_update_project_success(monkeypatch):
    """Update project info for a user's project: returns updated project"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    project_update = dummies.DummyProjectUpdate(name="UpdatedName", description="UpdatedDesc")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=True,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_update_project(
        db, project_id: int, name: str | None, description: str | None
    ):
        return dummies.DummyProject(id=project_id, name=name, description=description)

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_project, "update_project", fake_update_project)

    result = asyncio.run(
        update_project(
            project_id=project_id, project=project_update, user=user, db=None
        )
    )

    assert isinstance(result, dummies.DummyProject)
    assert result.id == project_id
    assert result.name == project_update.name
    assert result.description == project_update.description


def test_update_project_not_found(monkeypatch):
    """Update project not found: 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    project_update = dummies.DummyProjectUpdate(name="UpdatedName", description="UpdatedDesc")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return []
    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_project(
                project_id=project_id, project=project_update, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 404


def test_update_project_not_owner(monkeypatch):
    """Update project when not owner: 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    project_update = dummies.DummyProjectUpdate(name="UpdatedName", description="UpdatedDesc")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_project(
                project_id=project_id, project=project_update, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 404


def test_update_project_not_updated(monkeypatch):
    """Update project failed to update: 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    project_update = dummies.DummyProjectUpdate(name="UpdatedName", description="UpdatedDesc")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=True,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_update_project(
        db, project_id: int, name: str | None, description: str | None
    ):
        return []

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_project, "update_project", fake_update_project)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_project(
                project_id=project_id, project=project_update, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 404


def test_update_project_exception_is_project_from_user(monkeypatch):
    """Update project DB error when checking ownership -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    project_update = dummies.DummyProjectUpdate(name="UpdatedName", description="UpdatedDesc")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_project(
                project_id=project_id, project=project_update, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 500


def test_update_project_exception_update_project(monkeypatch):
    """Update project DB error when updating -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    project_update = dummies.DummyProjectUpdate(name="UpdatedName", description="UpdatedDesc")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=True,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_update_project(
        db, project_id: int, name: str | None, description: str | None
    ):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_project, "update_project", fake_update_project)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            update_project(
                project_id=project_id, project=project_update, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 500


def test_delete_project_success(monkeypatch):
    """Delete a user's project: returns deletion message"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=True,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_delete_project(db, project_id: int):
        return dummies.DummyProject(id=project_id, name="Project1", description="Desc1")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_project, "delete_project", fake_delete_project)

    result = asyncio.run(
        delete_project(project_id=project_id, user=user, db=None)
    )

    assert isinstance(result, dict)
    assert result.get("message") == f"Project with ID {project_id} deleted successfully"


def test_delete_project_not_found(monkeypatch):
    """Delete project not found: 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return []

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_project(
                project_id=project_id, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 404


def test_delete_project_not_owner(monkeypatch):
    """Delete project when not owner: 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_delete_project(db, project_id: int):
        return dummies.DummyProject(id=project_id, name="Project1", description="Desc1")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_project, "delete_project", fake_delete_project)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_project(
                project_id=project_id, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 404


def test_delete_project_not_deleted(monkeypatch):
    """Delete project failed to delete: 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_delete_project(db, project_id: int):
        return []

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(crud_project, "delete_project", fake_delete_project)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_project(
                project_id=project_id, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 404


def test_delete_project_exception_is_project_from_user(monkeypatch):
    """Delete project DB error when checking ownership -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            delete_project(
                project_id=project_id, user=user, db=None
            )
        )

    assert excinfo.value.status_code == 500


def test_get_project_documents_success(monkeypatch):
    """Get documents for a user's project: returns list of documents"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=True,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_get_documents_by_project(db, project_id: int):
        return [
            dummies.DummyDocument(id=1, name="doc1", url="url1"),
            dummies.DummyDocument(id=2, name="doc2", url="url2"),
        ]

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(
        crud_documents, "get_documents_by_project", fake_get_documents_by_project
    )

    result = asyncio.run(
        get_project_documents(project_id=project_id, user=user, db=None)
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "doc1"
    assert result[1].name == "doc2"


def test_get_project_documents_success_not_owner(monkeypatch):
    """Get documents for a user's project (not owner): returns documents"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_get_documents_by_project(db, project_id: int):
        return [
            dummies.DummyDocument(id=1, name="doc1", url="url1"),
            dummies.DummyDocument(id=2, name="doc2", url="url2"),
        ]

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(
        crud_documents, "get_documents_by_project", fake_get_documents_by_project
    )

    result = asyncio.run(
        get_project_documents(project_id=project_id, user=user, db=None)
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].name == "doc1"
    assert result[1].name == "doc2"


def test_get_project_documents_not_found(monkeypatch):
    """Get documents for a user's project: project not found -> 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return []

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_project_documents(project_id=project_id, user=user, db=None)
        )

    assert excinfo.value.status_code == 404


def test_get_project_documents_no_documents(monkeypatch):
    """Get documents for a user's project with no documents -> 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_get_documents_by_project(db, project_id: int):
        return []

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(
        crud_documents, "get_documents_by_project", fake_get_documents_by_project
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_project_documents(project_id=project_id, user=user, db=None)
        )

    assert excinfo.value.status_code == 404


def test_get_project_documents_exception_is_project_from_user(monkeypatch):
    """Get documents DB error when checking ownership -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_project_documents(project_id=project_id, user=user, db=None)
        )

    assert excinfo.value.status_code == 500


def test_get_project_documents_exception_get_documents_by_project(monkeypatch):
    """Get documents DB error retrieving documents -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_get_documents_by_project(db, project_id: int):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(
        crud_documents, "get_documents_by_project", fake_get_documents_by_project
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            get_project_documents(project_id=project_id, user=user, db=None)
        )

    assert excinfo.value.status_code == 500


def test_post_projects_documents_success(monkeypatch):
    """Upload document to a project: returns created document"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    file = dummies.DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_upload_file_to_s3(file):
        return "https://bucket.s3.amazonaws.com/mydoc.txt"

    async def fake_create_document(db, document_id: int, name: str, url: str):
        return dummies.DummyDocument(id=3, name=name, url=url)

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(controller, "upload_file_to_s3", fake_upload_file_to_s3)
    monkeypatch.setattr(
        crud_documents, "create_document", fake_create_document
    )

    response = asyncio.run(
        create_project_document(project_id=project_id, file=file, user=user, db=None)
    )

    assert response.id == 3
    assert response.name == file.filename
    assert response.url == "https://bucket.s3.amazonaws.com/mydoc.txt"


def test_post_projects_documents_not_found_project(monkeypatch):
    """Upload document: project not found -> 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    file = dummies.DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return []

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            create_project_document(project_id=project_id, file=file, user=user, db=None)
        )

    assert excinfo.value.status_code == 404


def test_post_projects_documents_fail_create_document(monkeypatch):
    """Upload document: create_document failed -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    file = dummies.DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_create_document(db, document_id: int, name: str, url: str):
        return []

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(
        crud_documents, "create_document", fake_create_document
    )

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            create_project_document(project_id=project_id, file=file, user=user, db=None)
        )

    assert excinfo.value.status_code == 500


def test_post_projects_documents_exception_is_project_from_user(monkeypatch):
    """Upload document DB error when checking project -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    file = dummies.DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            create_project_document(project_id=project_id, file=file, user=user, db=None)
        )

    assert excinfo.value.status_code == 500


def test_post_projects_documents_exception_create_document(monkeypatch):
    """Upload document DB error when creating document -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    file = dummies.DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_create_document(db, document_id: int, name: str, url: str):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(
        crud_documents, "create_document", fake_create_document
    )

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            create_project_document(project_id=project_id, file=file, user=user, db=None)
        )

    assert excinfo.value.status_code == 500


def test_post_projects_documents_exception_aws(monkeypatch):
    """Upload document AWS error while uploading -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    file = dummies.DummyUploadFile("mydoc.txt", b"hello world")

    async def fake_is_project_from_user(db, user_id: int, project_id: int):
        return dummies.DummyUserProject(
            is_owner=False,
            project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
        )

    async def fake_upload_file_to_s3(file):
        raise Exception("DB Error")

    async def fake_create_document(db, document_id: int, name: str, url: str):
        return dummies.DummyDocument(id=3, name=name, url=url)

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )
    monkeypatch.setattr(controller, "upload_file_to_s3", fake_upload_file_to_s3)
    monkeypatch.setattr(
        crud_documents, "create_document", fake_create_document
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            create_project_document(project_id=project_id, file=file, user=user, db=None)
        )

    assert excinfo.value.status_code == 500


def test_invite_user_to_project_success(monkeypatch):
    """Invite user to a project: returns success message"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    user_id_to_invite = 2

    class CallCounter:
        def __init__(self):
            self.count = 0

        async def fake_is_project_from_user(self, db, user_id: int, project_id: int):
            self.count += 1
            if self.count == 1:
                return dummies.DummyUserProject(
                    is_owner=True,
                    project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
                )
            else:
                return None

    counter = CallCounter()

    async def fake_create_user_project(db, user_project: dummies.DummyUserProjectCreate):
        return

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", counter.fake_is_project_from_user
    )

    monkeypatch.setattr(
        crud_user_project, "create_user_project", fake_create_user_project
    )

    response = asyncio.run(
        invite_user_to_project(
            project_id=project_id,
            user_id=user_id_to_invite,
            user=user,
            db=None
        )
    )

    assert response == {"message": f"User with ID {user_id_to_invite} invited to project {project_id} successfully"}


def test_invite_user_to_project_no_user_id(monkeypatch):
    """Invite user to a project: missing user_id -> 400"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            invite_user_to_project(
                project_id=project_id,
                user_id=None,
                user=user,
                db=None
            )
        )

    assert excinfo.value.status_code == 400


def test_invite_user_to_project_not_owner(monkeypatch):
    """Invite user to a project: not owner -> 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    user_id_to_invite = 2

    class CallCounter:
        def __init__(self):
            self.count = 0

        async def fake_is_project_from_user(self, db, user_id: int, project_id: int):
            self.count += 1
            if self.count == 1:
                return dummies.DummyUserProject(
                    is_owner=False,
                    project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
                )
            else:
                return None

    counter = CallCounter()

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", counter.fake_is_project_from_user
    )
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            invite_user_to_project(
                project_id=project_id,
                user_id=user_id_to_invite,
                user=user,
                db=None
            )
        )
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Project not found"


def test_invite_user_to_project_not_project(monkeypatch):
    """Invite user to a project: project not found -> 404"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    user_id_to_invite = 2

    class CallCounter:
        def __init__(self):
            self.count = 0

        async def fake_is_project_from_user(self, db, user_id: int, project_id: int):
            self.count += 1
            if self.count == 1:
                return None
            else:
                return None

    counter = CallCounter()

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", counter.fake_is_project_from_user
    )
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            invite_user_to_project(
                project_id=project_id,
                user_id=user_id_to_invite,
                user=user,
                db=None
            )
        )
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Project not found"


def test_invite_user_to_project_already_invited(monkeypatch):
    """Invite user to a project: already a member -> 400"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    user_id_to_invite = 2

    class CallCounter:
        def __init__(self):
            self.count = 0

        async def fake_is_project_from_user(self, db, user_id: int, project_id: int):
            self.count += 1
            if self.count == 1:
                return dummies.DummyUserProject(
                    is_owner=True,
                    project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
                )
            else:
                return dummies.DummyUserProject(
                    is_owner=False,
                    project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
                )

    counter = CallCounter()

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", counter.fake_is_project_from_user
    )
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            invite_user_to_project(
                project_id=project_id,
                user_id=user_id_to_invite,
                user=user,
                db=None
            )
        )
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "User is already a member of the project"


def test_invite_user_to_project_exception_is_project_from_user(monkeypatch):
    """Invite user DB error when checking membership -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    user_id_to_invite = 2

    async def fake_is_project_from_user(self, db, user_id: int, project_id: int):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", fake_is_project_from_user
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            invite_user_to_project(
                project_id=project_id,
                user_id=user_id_to_invite,
                user=user,
                db=None
            )
        )
    assert excinfo.value.status_code == 500


def test_invite_user_to_project_exception_is_project_from_user_case_2(monkeypatch):
    """Invite user DB error in the second membership check -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    user_id_to_invite = 2

    class CallCounter:
        def __init__(self):
            self.count = 0

        async def fake_is_project_from_user(self, db, user_id: int, project_id: int):
            self.count += 1
            if self.count == 1:
                return dummies.DummyUserProject(
                    is_owner=True,
                    project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
                )
            else:
                raise Exception("DB error")

    counter = CallCounter()

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", counter.fake_is_project_from_user
    )
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            invite_user_to_project(
                project_id=project_id,
                user_id=user_id_to_invite,
                user=user,
                db=None
            )
        )
    assert excinfo.value.status_code == 500


def test_invite_user_to_project_exception_create_user_project(monkeypatch):
    """Invite user DB error when creating user_project -> 500"""
    user = dummies.DummyUser(id=1, name="alice", password="secret")
    project_id = 1
    user_id_to_invite = 2

    class CallCounter:
        def __init__(self):
            self.count = 0

        async def fake_is_project_from_user(self, db, user_id: int, project_id: int):
            self.count += 1
            if self.count == 1:
                return dummies.DummyUserProject(
                    is_owner=True,
                    project=dummies.DummyProject(id=project_id, name="Project1", description="Desc1"),
                )
            else:
                return None

    counter = CallCounter()

    async def fake_create_user_project(db, user_project: dummies.DummyUserProjectCreate):
        raise Exception("DB error")

    monkeypatch.setattr(
        crud_user_project, "is_project_from_user", counter.fake_is_project_from_user
    )

    monkeypatch.setattr(
        crud_user_project, "create_user_project", fake_create_user_project
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            invite_user_to_project(
                project_id=project_id,
                user_id=user_id_to_invite,
                user=user,
                db=None
            )
        )
    assert excinfo.value.status_code == 500
