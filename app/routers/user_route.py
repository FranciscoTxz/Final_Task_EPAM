from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, SignUp, Login
from app.dependencies import get_db
from app.controllers import user_controller

router = APIRouter(prefix="/auth", tags=["users"])


@router.post("/signup", response_model=SignUp, status_code=201)
async def signup_user(user: UserCreate, db: Session = Depends(get_db)):
    return await user_controller.signup_user(user, db)


@router.post("/login", response_model=Login)
async def login_user(
    user: UserCreate, response: Response, db: Session = Depends(get_db)
):
    return await user_controller.login_user(user, response, db)
