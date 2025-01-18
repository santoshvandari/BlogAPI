from fastapi import APIRouter,Depends,HTTPException,status
from datetime import datetime
from dbconfig import get_db
from blog_utils import slug_genertor
from model import BlogPost,UserData
from motor.motor_asyncio import AsyncIOMotorDatabase
from utility import get_current_user




blogroute = APIRouter(prefix="/blog",tags=["Blog"])


@blogroute.post("/create")
async def create_blog(blogdata: BlogPost,db:AsyncIOMotorDatabase=Depends(get_db),current_user:UserData=Depends(get_current_user)):
    slug=await slug_genertor(blogdata.title,db)
    data = blogdata.dict()
    data.update({"slug":slug,"author":current_user["full_name"],"user_id":current_user["_id"],"created_at":datetime.now(),"updated_at":datetime.now()})
    result = await db["blogs"].insert_one(data)
    if result:
        return {"status":"Blog Created","blog":blogdata.dict()}
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Blog Creation Failed")