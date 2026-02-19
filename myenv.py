from functools import lru_cache
from fastapi import APIRouter, Depends
from pydantic_settings import BaseSettings

# 1. Definir el esquema de configuración
class Settings(BaseSettings):
    app_name: str = "Mi API FastAPI"
    admin_email: str = "admin@ejemplo.com"
    items_per_user: int = 50
    
    # Esto permite leer automáticamente de un archivo .env si existe
    class Config:
        env_file = ".env"

env_router = APIRouter()

# 2. Dependencia para obtener la configuración (cacheada)
@lru_cache
def get_settings():
    return Settings()

# 3. Endpoint para demostrar el acceso a las claves desde el código
@env_router.get("/info")
async def get_env_info(settings: Settings = Depends(get_settings)):
    return {
        "application": settings.app_name,
        "contact": settings.admin_email,
        "limit": settings.items_per_user
    }