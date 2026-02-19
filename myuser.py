import uuid
from typing import  AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from database.database import Base

# Configuración Async para FastAPI Users (requiere: pip install aiomysql)
# Usamos una conexión asíncrona paralela a la síncrona de database.py
DATABASE_URL_ASYNC = "mysql+aiomysql://root:@localhost:3306/pruebas"
engine_async = create_async_engine(DATABASE_URL_ASYNC)
async_session_maker = sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)
# DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/pruebas"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La dependencia que usa FastAPI Users
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session # Aquí se entrega la sesión asíncrona

# 1. Definir el modelo de usuario (SQLAlchemy)
class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"

# 2. Schemas Pydantic
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

# 4. Configurar el backend de autenticación (JWT)
SECRET = "SUPER_SECRET_KEY"  # ¡Cambiar en producción!

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# 5. Router unificado
auth_router = APIRouter()

# Rutas de API (JSON)
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Autenticación API"]
)
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Autenticación API"]
)

# Rutas de Vistas (HTML)
templates = Jinja2Templates(directory="templates")

@auth_router.get("/login", response_class=HTMLResponse, tags=["Vistas"])
async def login_view(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.get("/register", response_class=HTMLResponse, tags=["Vistas"])
async def register_view(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@auth_router.get("/dashboard", response_class=HTMLResponse, tags=["Vistas"])
async def dashboard_view(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})