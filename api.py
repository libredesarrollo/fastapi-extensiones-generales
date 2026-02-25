from contextlib import asynccontextmanager
from fastapi import FastAPI
import redis.asyncio as redis
# import fastapi_limiter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# Importamos tus routers
from myemail import email_router
from myuser import auth_router
from myenv import env_router
from mylimiter import limiter_router
from mylogging import logging_router
from mycache import cache_router


from database.database import Base, engine, get_database_session
from mycrud import MyCRUDRouter,SQLCRUDRouter, Category, Task, CategoryModel
#uvicorn api:app --reload     

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- INICIO (Infrastructure Setup) ---
    # Conexión a Redis
    redis_instance = redis.from_url(
        "redis://localhost:6379", 
        encoding="utf-8", 
        decode_responses=True
    )
    
    # Inicializar FastAPI Cache con el backend de Redis
    FastAPICache.init(RedisBackend(redis_instance), prefix="fastapi-cache")
    
    # # Inicializar el limitador (usando la referencia al módulo si la clase falla)
    # await fastapi_limiter.FastAPILimiter.init(redis_instance)
    
    yield  # Aquí es donde la app "corre"
    
    # --- CIERRE (Cleanup) ---
    await redis_instance.close()

app = FastAPI(lifespan=lifespan)

CategoryModel.metadata.create_all(bind=engine)
#QUITAR SI USAS Alembic
Base.metadata.create_all(bind=engine)

# @router.get('/hello')
# def hello_world(db: Session = Depends(get_database_session)):
#     return { "hello": "world" }

app.include_router(email_router, prefix='/email')
app.include_router(auth_router, prefix='/user')
app.include_router(env_router, prefix='/config')
app.include_router(limiter_router, prefix='/limiter')
app.include_router(logging_router, prefix='/logging')
app.include_router(cache_router, prefix='/cache')

# app.include_router(
#     MyCRUDRouter(schema=Category, prefix="/categories", tags=["Categories"])
# )
app.include_router(
    MyCRUDRouter(schema=Task, prefix="/tasks", tags=["Tasks"])
)
app.include_router(
    SQLCRUDRouter(schema=Category, 
                  model=CategoryModel,
                  get_db_func=get_database_session, 
                  prefix="/categories", tags=["Categories"])
)