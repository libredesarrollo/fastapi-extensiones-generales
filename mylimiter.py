from fastapi import APIRouter, Depends
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter


limiter_router = APIRouter()

# pip install fastapi-limiter redis

# Endpoint con límite: Máximo 2 peticiones cada 5 segundos
@limiter_router.get("/test", dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 5))))])
async def limiter_test():
    return {
        "message": "Acceso permitido",
        "info": "Este endpoint permite máximo 2 peticiones cada 5 segundos."
    }

# Endpoint con límite estricto: 1 petición cada 10 segundos
@limiter_router.get("/heavy", dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(1, Duration.SECOND * 10))))])
async def heavy_task(
    # _ = Depends(RateLimiter(times=1, seconds=10))
):
    return {
        "message": "Tarea pesada iniciada",
        "info": "Límite estricto: 1 petición cada 10 segundos."
    }

