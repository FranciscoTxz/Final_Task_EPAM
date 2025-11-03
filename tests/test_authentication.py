import app.controllers.authentication as authentication_module
from app.crud import user_crud as crud_user
import jwt
import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from tests.test_users import DummyUser
import asyncio


def test_get_authentication_user_header_success(monkeypatch):
    """get_authentication_user returns the user when the token is valid"""
    # prepare JWT token with the same SECRET_KEY as the module
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"username": "alice", "user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    async def fake_get_user_by_name(db, name: str):
        return DummyUser(id=1, name=name, password="hashed")

    # patch the CRUD function used by the module
    monkeypatch.setattr(crud_user, "get_user_by_name", fake_get_user_by_name)

    # Call the dependency directly, passing the Authorization header
    result = asyncio.run(
        authentication_module.get_authentication_user(
            session_token=None, authorization=f"Bearer {token}", db=None
        )
    )

    assert isinstance(result, DummyUser)
    assert result.id == 1
    assert result.name == "alice"


def test_get_authentication_user_cookie_success(monkeypatch):
    """get_authentication_user returns the user when the token is valid"""
    # prepare JWT token with the same SECRET_KEY as the module
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"username": "alice", "user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    async def fake_get_user_by_name(db, name: str):
        return DummyUser(id=1, name=name, password="hashed")

    # patch the CRUD function used by the module
    monkeypatch.setattr(crud_user, "get_user_by_name", fake_get_user_by_name)

    # Call the dependency directly, passing the session cookie token
    result = asyncio.run(
        authentication_module.get_authentication_user(
            session_token=token, authorization=None, db=None
        )
    )

    assert isinstance(result, DummyUser)
    assert result.id == 1
    assert result.name == "alice"


def test_get_authentication_user_no_token(monkeypatch):
    """get_authentication_user without token: raises HTTPException 401"""

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            authentication_module.get_authentication_user(
                session_token=None, authorization=None, db=None
            )
        )

    assert excinfo.value.status_code == 401


def test_get_authentication_user_no_user(monkeypatch):
    """get_authentication_user with invalid token: raises HTTPException 401"""
    # prepare JWT token with the same SECRET_KEY as the module
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            authentication_module.get_authentication_user(
                session_token=token, authorization=None, db=None
            )
        )

    assert excinfo.value.status_code == 401


def test_get_authentication_user_no_user_in_db(monkeypatch):
    """get_authentication_user with invalid token: raises HTTPException 401"""
    # prepare JWT token with the same SECRET_KEY as the module
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"username": "alice", "user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    async def fake_get_user_by_name(db, name: str):
        return []  # user not found

    # patch the CRUD function used by the module
    monkeypatch.setattr(crud_user, "get_user_by_name", fake_get_user_by_name)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            authentication_module.get_authentication_user(
                session_token=token, authorization=None, db=None
            )
        )

    assert excinfo.value.status_code == 401


def test_get_authentication_exception(monkeypatch):
    """get_authentication_user with exception"""
    # prepare JWT token with the same SECRET_KEY as the module
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"username": "alice", "user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    async def fake_get_user_by_name(db, name: str):
        raise Exception("DB error")

    # patch the CRUD function used by the module
    monkeypatch.setattr(crud_user, "get_user_by_name", fake_get_user_by_name)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            authentication_module.get_authentication_user(
                session_token=token, authorization=None, db=None
            )
        )

    assert excinfo.value.status_code == 500
