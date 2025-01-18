from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import jwt
from dbconfig import get_db
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase
from model import TokenData
from jwt.exceptions import InvalidTokenError


SECRET_KEY= "618073637e60f15b5046c6047f709d26e4b47e9ef86f2e7426506e363799cc672e7d43bd52b6c6c46f969ab662befafc5f71193f6b6c47e93ee6e78085e77d5b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context= CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_password_hash(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str):
    return pwd_context.verify(plain_password,hashed_password)

async def get_user(username:str,db:AsyncIOMotorDatabase):
    user = await db["users"].find_one({"username":username})
    if user:
        return user
    return None

async def authenticate_user(username:str,password:str,db:AsyncIOMotorDatabase):
    user = await get_user(username,db)
    if not user:
        return False
    if not verify_password(password,user["password"]):
        return False
    return user

def create_access_token(data:dict):
    to_encode = data.copy()
    expire= datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)


async def get_current_user(token:str = Depends(oauth2_scheme),db:AsyncIOMotorDatabase=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(username=token_data.username,db=db)
    if user is None:
        raise credentials_exception
    user.pop("password")
    return user



async def create_user(username:str,fullname:str,password:str,email:str,db:AsyncIOMotorDatabase):
    hashed_password = get_password_hash(password)
    data={
        "username":username,
        "password":hashed_password,
        "email":email,
        "full_name":fullname,
        "created_at":datetime.now()
    }
    if await db.users.find_one({"username":username}):
        raise HTTPException(status_code=400,detail="Username already exists")
    try:
        await db["users"].insert_one(data)
    except Exception:
        raise HTTPException(status_code=500,detail="Something went wrong")
    data.pop("password")
    return data         
