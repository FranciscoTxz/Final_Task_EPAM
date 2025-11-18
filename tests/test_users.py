import pytest
from app.routers.user_route import signup_user, login_user
import app.controllers.user_controller as user_controller
from app.schemas.user_schema import UserCreate
from app.crud import user_crud
from fastapi import HTTPException, Response
import asyncio
from hashlib import sha1
import tests.dummies as dummies


def test_signup_success(monkeypatch):
    """Happy case: new user -> created successfully"""

    test_user = UserCreate(name="alice", password="secret")

    async def fake_get_user_by_name(db, name: str):
        return None

    async def fake_create_user(db, user):
        # simulate returning the created user
        return dummies.DummyUser(id=1, name=user.name, password=user.password)

    monkeypatch.setattr(user_crud, "get_user_by_name", fake_get_user_by_name)
    monkeypatch.setattr(user_crud, "create_user", fake_create_user)

    result = asyncio.run(signup_user(test_user, db=None))

    assert isinstance(result, dict)
    assert result.get("message") == "User created successfully"


def test_signup_existing_user(monkeypatch):
    """If the name already exists, raises HTTPException with status 400"""

    test_user = UserCreate(name="bob", password="secret")

    async def fake_get_user_by_name(db, name: str):
        return dummies.DummyUser(id=2, name=name, password="hashed")

    monkeypatch.setattr(user_crud, "get_user_by_name", fake_get_user_by_name)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(signup_user(test_user, db=None))

    assert excinfo.value.status_code == 400


def test_signup_no_name(monkeypatch):
    """If no name is provided, raises HTTPException with status 400"""

    test_user = UserCreate(name="", password="secret")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(signup_user(test_user, db=None))

    assert excinfo.value.status_code == 400


def test_signup_exception(monkeypatch):
    """If there's a DB error, raises HTTPException with status 500"""

    test_user = UserCreate(name="bob", password="secret")

    async def fake_get_user_by_name(db, name: str):
        raise Exception("DB error")

    monkeypatch.setattr(user_crud, "get_user_by_name", fake_get_user_by_name)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(signup_user(test_user, db=None))

    assert excinfo.value.status_code == 500


def test_login_success(monkeypatch):
    """Successful login: returns token and sets cookie/Authorization"""

    test_user = UserCreate(name="alice", password="secret")

    # existing user with hashed password
    async def fake_get_user_by_name(db, name: str):
        return dummies.DummyUser(id=1, name=name, password=sha1("secret".encode()).hexdigest())

    monkeypatch.setattr(user_crud, "get_user_by_name", fake_get_user_by_name)
    # ensure SECRET_KEY in the module where it's used
    monkeypatch.setattr(user_controller, "SECRET_KEY", "testskey")

    response = Response()
    result = asyncio.run(login_user(test_user, response, db=None))

    assert isinstance(result, dict)
    assert result.get("message") == "Login successful"
    token = result.get("access_token")
    assert token is not None
    assert response.headers.get("Authorization") == f"Bearer {token}"
    set_cookie = response.headers.get("set-cookie", "")
    assert "session_token" in set_cookie


def test_login_wrong_password(monkeypatch):
    """If password is incorrect, must raise HTTPException 400"""

    test_user = UserCreate(name="bob", password="wrongpass")

    async def fake_get_user_by_name(db, name: str):
        # stored password is different
        return dummies.DummyUser(id=2, name=name, password="someotherhash")

    monkeypatch.setattr(user_crud, "get_user_by_name", fake_get_user_by_name)
    monkeypatch.setattr(user_controller, "SECRET_KEY", "testskey")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(login_user(test_user, Response(), db=None))

    assert excinfo.value.status_code == 400


def test_login_user_not_found(monkeypatch):
    """If the user doesn't exist, must raise HTTPException 404"""

    test_user = UserCreate(name="noexist", password="secret")

    async def fake_get_user_by_name(db, name: str):
        return None

    monkeypatch.setattr(user_crud, "get_user_by_name", fake_get_user_by_name)
    monkeypatch.setattr(user_controller, "SECRET_KEY", "testskey")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(login_user(test_user, Response(), db=None))

    assert excinfo.value.status_code == 404


def test_login_not_name(monkeypatch):
    """If no name is provided, raises HTTPException with status 400"""

    test_user = UserCreate(name="", password="secret")

    monkeypatch.setattr(user_controller, "SECRET_KEY", "testskey")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(login_user(test_user, Response(), db=None))

    assert excinfo.value.status_code == 400


def test_login_user_exception(monkeypatch):
    """In case of a DB error, raises HTTPException 500"""

    test_user = UserCreate(name="noexist", password="secret")

    async def fake_get_user_by_name(db, name: str):
        raise Exception("DB error")

    monkeypatch.setattr(user_crud, "get_user_by_name", fake_get_user_by_name)
    monkeypatch.setattr(user_controller, "SECRET_KEY", "testskey")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(login_user(test_user, Response(), db=None))

    assert excinfo.value.status_code == 500
