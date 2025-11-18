from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from ..config import SECRET_KEY
import jwt
from app.crud import user_crud as crud_user


async def get_authentication_user(
    session_token: str = Cookie(None),
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Return the authenticated user from a JWT found in the Authorization header (Bearer) or a session cookie.

    Args:
        session_token: Optional session token read from the 'session_token' cookie, used if no Bearer token is provided.
        authorization: Optional HTTP Authorization header value in the form 'Bearer <token>'.
        db: Async SQLAlchemy session dependency used to fetch the user.

    Returns:
        The authenticated user instance retrieved from the database.

    Raises:
        HTTPException: With status code 401 if no token is provided, the token is invalid,
        or the user cannot be found; with status code 500 for unexpected authentication errors.
    """

    token = None

    if authorization:
        scheme, _, param = authorization.partition(" ")
        if scheme.lower() == "bearer" and param:
            token = param

    if not token and session_token:
        token = session_token

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        username = payload.get("username")
        if not user_id or not username:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = await crud_user.get_user_by_name(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")
    return user
