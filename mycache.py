from fastapi import APIRouter
from fastapi_cache.decorator import cache
import asyncio
from datetime import datetime

cache_router = APIRouter()

# Este endpoint cacheará la respuesta durante 60 segundos.
# La primera vez tardará 3 segundos (simulando carga), las siguientes serán instantáneas.
@cache_router.get("/heavy-task")
@cache(expire=60)
async def heavy_task():
    # Simula un proceso pesado (consulta a DB lenta, cálculo complejo, etc.)
    await asyncio.sleep(3)
    print('*****')
    return {
        "message": "Datos procesados (cacheado por 60s)",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "info": "Si la hora 'generated_at' no cambia en la siguiente petición, estás viendo el caché."
    }