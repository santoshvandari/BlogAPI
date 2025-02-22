from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from dbconfig import get_db
from model import PasswordUpdate, Token,UserData,UserCreate, UserUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from utility import authenticate_user,create_access_token,create_user, get_current_user,get_password_hash


auth = APIRouter(prefix="/auth",tags=["Authentication"])

@auth.post("/token",response_model=Token)
async def login_for_access_token(formdata: OAuth2PasswordRequestForm = Depends(),db:AsyncIOMotorDatabase=Depends(get_db)):
    user = await authenticate_user(formdata.username,formdata.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED ,detail="Invalid Credentials")
    access_token = create_access_token(data={"username":user["username"]})
    return {"access_token":access_token,"token_type":"bearer"}
    

@auth.post("/register",response_model=Token)
async def register_user(user:UserCreate,db:AsyncIOMotorDatabase=Depends(get_db)):
    user=await create_user(user.username,user.fullname,user.password,user.email,db)
    if user:
        access_token=create_access_token(data={"username":user['username']})
        return Token(access_token=access_token,token_type="bearer")
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Already Exists")

@auth.get("/users/me")
async def read_users_me(current_user:UserData=Depends(get_current_user),db:AsyncIOMotorDatabase=Depends(get_db)):
    id = current_user["_id"]
    blogs = await db["blogs"].find({"user_id":id},{"_id":0,"user_id":0}).to_list()
    current_user.update({"blogs":blogs})
    current_user.pop("_id")
    return {"data":current_user}

@auth.put("/users/update")
async def update_user(user:UserUpdate,current_user:UserData=Depends(get_current_user),db:AsyncIOMotorDatabase=Depends(get_db)):
    # remove unset or empty data 
    user = user.dict(exclude_unset=True)
    if not user:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No Data to Update")
    id = current_user["_id"]
    res = await db["users"].update_one({"_id":id},{"$set":user})
    if res.modified_count:
        return {"message":"User Updated Successfully"}
    return {"message":"User Not Updated"}

@auth.put("/users/changepassword")
async def change_password(password:PasswordUpdate,current_user:UserData=Depends(get_current_user),db:AsyncIOMotorDatabase=Depends(get_db)):
    id = current_user["_id"]
    if not password:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No Password Provided")
    
    if password.updatedpw != password.confirmpwd:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password Confirm Mismatch")
    
    userauth = await authenticate_user(current_user["username"],password.currentpwd,db)
    if not userauth:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Existing Password")
    hashedpw = get_password_hash(password.updatedpw)

    res = await db["users"].update_one({"_id":id},{"$set":{"password":hashedpw}})
    if res.modified_count:
        return {"message":"Password Changed Successfully"}
    return {"message":"Password Not Changed"}