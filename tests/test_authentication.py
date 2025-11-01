import app.controllers.authentication as authentication_module
from app.crud import user_crud as crud_user
import jwt
import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from tests.test_users import DummyUser
import asyncio


def test_get_authentication_user_header_success(monkeypatch):
    """get_authentication_user devuelve el usuario cuando el token es válido"""
    # preparar token JWT con la misma SECRET_KEY que el módulo
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"username": "alice", "user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    async def fake_get_user_by_name(db, name: str):
        return DummyUser(id=1, name=name, password="hashed")

    # parchear la función CRUD usada por el módulo
    monkeypatch.setattr(crud_user, "get_user_by_name", fake_get_user_by_name)

    # Llamar directamente a la dependencia pasando el header Authorization
    result = asyncio.run(
        authentication_module.get_authentication_user(
            session_token=None, authorization=f"Bearer {token}", db=None
        )
    )

    assert isinstance(result, DummyUser)
    assert result.id == 1
    assert result.name == "alice"


def test_get_authentication_user_cookie_success(monkeypatch):
    """get_authentication_user devuelve el usuario cuando el token es válido"""
    # preparar token JWT con la misma SECRET_KEY que el módulo
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"username": "alice", "user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    async def fake_get_user_by_name(db, name: str):
        return DummyUser(id=1, name=name, password="hashed")

    # parchear la función CRUD usada por el módulo
    monkeypatch.setattr(crud_user, "get_user_by_name", fake_get_user_by_name)

    # Llamar directamente a la dependencia pasando el header Authorization
    result = asyncio.run(
        authentication_module.get_authentication_user(
            session_token=token, authorization=None, db=None
        )
    )

    assert isinstance(result, DummyUser)
    assert result.id == 1
    assert result.name == "alice"


def test_get_authentication_user_no_token(monkeypatch):
    """get_authentication_user sin token: lanza HTTPException 401"""

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            authentication_module.get_authentication_user(
                session_token=None, authorization=None, db=None
            )
        )

    assert excinfo.value.status_code == 401


def test_get_authentication_user_no_user(monkeypatch):
    """get_authentication_user con token inválido: lanza HTTPException 401"""
    # preparar token JWT con la misma SECRET_KEY que el módulo
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
    """get_authentication_user con token inválido: lanza HTTPException 401"""
    # preparar token JWT con la misma SECRET_KEY que el módulo
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"username": "alice", "user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    async def fake_get_user_by_name(db, name: str):
        return []  # usuario no encontrado

    # parchear la función CRUD usada por el módulo
    monkeypatch.setattr(crud_user, "get_user_by_name", fake_get_user_by_name)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            authentication_module.get_authentication_user(
                session_token=token, authorization=None, db=None
            )
        )

    assert excinfo.value.status_code == 401


def test_get_authentication_exception(monkeypatch):
    """get_authentication_user con exception"""
    # preparar token JWT con la misma SECRET_KEY que el módulo
    monkeypatch.setattr(authentication_module, "SECRET_KEY", "testskey")

    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"username": "alice", "user_id": 1, "exp": expire},
        "testskey",
        algorithm="HS256",
    )

    async def fake_get_user_by_name(db, name: str):
        raise Exception("DB error")

    # parchear la función CRUD usada por el módulo
    monkeypatch.setattr(crud_user, "get_user_by_name", fake_get_user_by_name)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            authentication_module.get_authentication_user(
                session_token=token, authorization=None, db=None
            )
        )

    assert excinfo.value.status_code == 500
