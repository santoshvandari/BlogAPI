from typing import Optional
from datetime import datetime
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

class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


class BlogPost(BaseModel):
    title: str
    content: str
    tag : str
    status: Optional[str] = "published"

class BlogData(BaseModel):
    title: str
    slug : str
    content: str
    tag: str
    author : str
    created_at: datetime
    updated_at: datetime
    author: str

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tag: Optional[str] = None
    status: Optional[str] = None
