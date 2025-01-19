from fastapi import APIRouter,Depends,HTTPException,status
from datetime import datetime
from dbconfig import get_db
from blog_utils import slug_genertor
from model import BlogPost, BlogUpdate,UserData,BlogData
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


@blogroute.get("/all")
async def get_all_blogs(current_user:UserData=Depends(get_current_user),db:AsyncIOMotorDatabase=Depends(get_db)):
    blogs = await db["blogs"].find({"user_id":current_user["_id"]},{"_id":0,"user_id":0}).to_list()
    return blogs

@blogroute.patch("/update/{slug}")
async def update_blog(slug:str,blogdata:BlogUpdate,db:AsyncIOMotorDatabase=Depends(get_db),current_user:UserData=Depends(get_current_user)):
    data = blogdata.dict(exclude_unset=True)
    if not data:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No data to update")
    blog=await db["blogs"].find_one({"slug":slug,"user_id":current_user["_id"]})
    if not blog:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Blog Not Found")
    if blog["user_id"]!=current_user["_id"]:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You are not the author of this blog")
    data.update({"updated_at":datetime.now()})
    data=blogdata.dict(exclude_unset=True)
    result = await db["blogs"].update_one({"slug":slug},{"$set":data})
    if result:
        return {"result":"Blog Updated"}
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Blog Update Failed")


@blogroute.delete("/delete/{slug}")
async def delete_blog(slug:str,db:AsyncIOMotorDatabase=Depends(get_db),current_user:UserData=Depends(get_current_user)):
    blog = await db["blogs"].find_one({"slug":slug,"user_id":current_user["_id"]})
    if not blog:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Blog Not Found")
    if blog["user_id"]!=current_user["_id"]:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You are not the author of this blog")
    result = await db["blogs"].delete_one({"slug":slug,"user_id":current_user["_id"]})
    if result:
        return {"result":"Blog Deleted"}
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Blog Deletion Failed")
