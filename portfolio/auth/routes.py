import sqlalchemy
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from oauth import Hasher, create_access_token, CustomHTTPBearer
from schemas import UserIn, UserOut
from database import metadata, database, DATABASE_URL
from models import user, clothe


app = FastAPI()

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

oauth2_schema = CustomHTTPBearer()


@app.on_event("startup")
async def start_up():
    await database.connect()


@app.on_event("shutdown")
async def teardown():
    await database.disconnect()


@app.post('/create_user/')
async def create_user(request: UserIn):
    request.password = Hasher.hash_password(request.password)
    new_user = user.insert().values(**request.dict())
    commit = await database.execute(new_user)
    user_created = await database.fetch_one(user.select().where(user.c.id == commit))
    token = create_access_token(user_created)
    return {"token": token}


@app.get("/clothes/", dependencies=[Depends(oauth2_schema)])
async def get_all_clothes():
    result = await database.fetch_all(clothe.select())
    return result


@app.post('/clothes/', dependencies=[Depends(HTTPBearer), Depends(oauth2_schema)])
async def create_cloth(request: Request):
    clothe_created = clothe.insert().values(**request.dict())

    pass
