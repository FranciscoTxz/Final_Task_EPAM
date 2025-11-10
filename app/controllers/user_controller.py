from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Response
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schema import UserCreate
from app.crud import user_crud as crud_user
from hashlib import sha1
from ..config import SECRET_KEY


async def signup_user(user: UserCreate, db: AsyncSession):
    """Create a new user account after validating input and ensuring the username is unique.

    Args:
        user: Incoming user payload with name and password.
        db: Async SQLAlchemy session used for database access.

    Returns:
        message: A message confirming successful user creation.

    Raises:
        HTTPException: 400 if required fields are missing or the name is already registered; 500 on unexpected errors.
    """
    try:
        if not user.name or not user.password:
            raise HTTPException(status_code=400, detail="Name and password are required")
        db_user = await crud_user.get_user_by_name(db, name=user.name)
        if db_user:
            raise HTTPException(status_code=400, detail="Name already registered")
        user.password = sha1(user.password.encode()).hexdigest()
        await crud_user.create_user(db, user)
        return {"message": "User created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


async def login_user(user: UserCreate, response: Response, db: AsyncSession):
    """Authenticate a user, issue a short-lived JWT, and set it in both a cookie and the Authorization header.

    Args:
        user: Incoming user payload with name and password.
        response: FastAPI Response used to set the session cookie and headers.
        db: Async SQLAlchemy session used for database access.

    Returns:
        message: A message confirming successful login.
        access_token: The generated JWT access token.

    Raises:
        HTTPException: 400 for missing fields or incorrect password; 404 if the user is not found;
        500 on unexpected errors.
    """
    try:
        if not user.name or not user.password:
            raise HTTPException(status_code=400, detail="Name and password are required")
        db_user = await crud_user.get_user_by_name(db, name=user.name)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if db_user.password != sha1(user.password.encode()).hexdigest():
            raise HTTPException(status_code=400, detail="Incorrect password")
        # JWT token generation 1 hour expiration
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        token = jwt.encode(
            {"username": user.name, "user_id": db_user.id, "exp": expire},
            SECRET_KEY,
            algorithm="HS256",
        )
        response.set_cookie(key="session_token", value=token, httponly=True, max_age=3600)
        response.headers["Authorization"] = f"Bearer {token}"
        return {"message": "Login successful", "access_token": token}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
