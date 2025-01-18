from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class loginData(BaseModel):
    username: str
    password: str


class UserData(BaseModel):
    fullname : str
    username: str
    email: str

class UserCreate(UserData):
    password: str