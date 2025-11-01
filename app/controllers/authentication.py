from fastapi import Cookie, Depends, Header, HTTPException
from pytest import Session
from app.dependencies import get_db
from ..config import SECRET_KEY
import jwt
from app.crud import user_crud as crud_user


async def get_authentication_user(
    session_token: str = Cookie(None),
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
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
