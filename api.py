from contextlib import asynccontextmanager
from fastapi import FastAPI
import redis.asyncio as redis
# import fastapi_limiter
from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend

# Importamos tus routers
from myemail import email_router
from myuser import auth_router
from myenv import env_router
from mylimiter import limiter_router
from mylogging import logging_router

from mycrud import MyCRUDRouter, Category, Task
from mystreaming import streaming_router

from mycelery import celery_router
from mycache import cache_router


from fastapi_cache.backends.inmemory import InMemoryBackend

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
    # FastAPICache.init(RedisBackend(redis_instance), prefix="fastapi-cache")
    
    # Inicializar FastAPI Cache con el backend en Memoria
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    
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

app.include_router(streaming_router, prefix='/stream', tags=["Streaming"])
app.include_router(celery_router, prefix='/celery', tags=["Celery"])

app.include_router(cache_router, prefix='/cache')


# app.include_router(
#     MyCRUDRouter(schema=Category, prefix="/categories", tags=["Categories"])
# )
app.include_router(
    MyCRUDRouter(schema=Task, prefix="/tasks", tags=["Tasks"])
)
app.include_router(
    SQLCRUDRouter(schema=Category, model=CategoryModel,get_db_func=get_database_session, prefix="/categories", tags=["Categories"])
)

#pip install "celery[redis]" fastapi uvicorn
# Terminal 1 (La API):
# uvicorn main:app --reload

# Terminal 2 (El Worker):

# celery -A mycelery.celery_app worker --loglevel=info


# - -A (o --app): Es el "Argumento de Aplicación". Le dice a Celery: "Busca mi configuración aquí".
# Haz un POST a http://127.0.0.1:8000/celery/run-task/Andres.
# Recibirás un task_id inmediatamente.
# Mira la Terminal 2, verás que el worker dice "Iniciando tarea...".
# Espera 10 segundos.
# Consulta http://127.0.0.1:8000/celery/status/{task_id} para ver el resultado "SUCCESS".
