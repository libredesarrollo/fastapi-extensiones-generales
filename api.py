from fastapi import FastAPI, Depends, APIRouter, Query, Path
from sqlalchemy.orm import Session

from database.database import Base, engine, get_database_session
#uvicorn api:app --reload

from myemail import email_router
from myuser import auth_router
from myenv import env_router

app = FastAPI()
router = APIRouter()

#QUITAR SI USAS Alembic
# Base.metadata.create_all(bind=engine)

# @router.get('/hello')
# def hello_world(db: Session = Depends(get_database_session)):
#     return { "hello": "world" }

app.include_router(email_router, prefix='/email')
app.include_router(auth_router, prefix='/user')
app.include_router(env_router, prefix='/config')