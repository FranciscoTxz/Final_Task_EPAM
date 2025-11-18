from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user_schema import UserCreate, SignUp, Login
from app.dependencies import get_db
from app.controllers import user_controller

router = APIRouter(prefix="/auth", tags=["users"])


@router.post("/signup", response_model=SignUp, status_code=201)
async def signup_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    return await user_controller.signup_user(user, db)


@router.post("/login", response_model=Login)
async def login_user(
    user: UserCreate, response: Response, db: AsyncSession = Depends(get_db)
):
    """Authenticate a user and issue a JWT."""
    return await user_controller.login_user(user, response, db)
