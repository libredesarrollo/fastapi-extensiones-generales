from fastapi import APIRouter
from loguru import logger
import sys

# --- Configuración de Loguru ---

# 1. Quitar el handler por defecto para evitar duplicados si se reconfigura.
logger.remove()

# 2. Añadir un handler para la consola (stderr) con formato y colores.
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

# 3. Añadir un handler para guardar los logs en un archivo.
#    - rotation="10 MB": Rota el archivo cuando alcanza los 10 MB.
#    - retention="7 days": Conserva los archivos de log por 7 días.
#    - compression="zip": Comprime los archivos de log antiguos.
#    - level="DEBUG": Guarda logs desde el nivel DEBUG hacia arriba en el archivo.
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    encoding="utf-8"
)

# --- Router de FastAPI ---

logging_router = APIRouter()

@logging_router.get("/info")
async def log_info():
    """Endpoint que registra un mensaje informativo."""
    logger.info("Este es un mensaje informativo desde el endpoint /info.")
    return {"message": "Mensaje informativo registrado. Revisa la consola o 'logs/app.log'."}

@logging_router.get("/error")
async def log_error():
    """Endpoint que simula un error y lo registra con su traceback."""
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("¡Ocurrió un error! Se intentó dividir por cero.")
    return {"message": "Error registrado con traceback. Revisa la consola o 'logs/app.log'."}

@logging_router.get("/debug/{user_id}")
async def log_debug(user_id: int):
    """Endpoint que registra un mensaje de depuración con datos contextuales."""
    user_data = {"id": user_id, "name": f"Usuario_{user_id}"}
    logger.debug(f"Procesando solicitud para el usuario: {user_data}")
    return {"message": f"Mensaje de depuración registrado para el usuario {user_id}."}
