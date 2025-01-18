from fastapi import FastAPI
from authroute import auth
from blogroute import blogroute
from dbconfig import initialize_db,db_shutdown

app = FastAPI()

@app.on_event("startup")
async def startup():
    await initialize_db()

@app.on_event("shutdown")
async def shutdown():
    await db_shutdown()

app.include_router(auth)

@app.get("/")
def read_root():
    return {"Hello":"World"}
