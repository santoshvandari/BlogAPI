from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

try:
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.blog
except Exception:
    raise HTTPException(status_code=500,detail="Database Connection Error")

async def initialize_db():
    try:
        if "users" not in await db.list_collection_names():
            await db.create_collection("users")
        if "blogs" not in await db.list_collection_names():
            await db.create_collection("blogs")
    except Exception:
        raise HTTPException(status_code=500,detail="Database Connection Error")
    
async def get_db():
        yield db
   
async def db_shutdown():
    try:
        client.close()
    except Exception:
        raise HTTPException(status_code=500,detail="Database Connection Error")