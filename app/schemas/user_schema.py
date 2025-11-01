from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    password: str


class UserCreate(UserBase):
    pass


class SignUp(BaseModel):
    message: str


class Login(BaseModel):
    message: str
    access_token: str
