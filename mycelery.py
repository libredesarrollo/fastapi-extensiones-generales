from celery import Celery
from fastapi import APIRouter
import time

# --- 1. Configuración de Celery (El Broker y Backend) ---
# Definimos la instancia de Celery.
# broker: El "buzón" donde FastAPI deja los mensajes (Redis).
# backend: Donde el worker guarda los resultados para que FastAPI los lea después (Redis).
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# --- 2. El Trabajador (Worker) ---
# Esta función NO se ejecuta en el servidor de FastAPI.
# Se ejecuta en el proceso separado de Celery (el "sótano").
@celery_app.task
def slow_task(name: str):
    print(f"Iniciando tarea pesada para: {name}")
    time.sleep(10)  # Simula un proceso de 10 segundos (ej. generar un PDF, procesar video)
    return f"¡Tarea completada para {name}!"

# --- 3. El Productor (FastAPI) ---
celery_router = APIRouter()

# @celery_router.post("/run-task/{name}")
@celery_router.get("/run-task/{name}")
async def run_background_task(name: str):
    """
    Endpoint que recibe la petición y la delega a Celery.
    Retorna inmediatamente el ID de la tarea, sin esperar a que termine.
    """
    # .delay() es la clave: envía el mensaje a Redis y retorna al instante.
    task = slow_task.delay(name)
    
    return {
        "message": "Tarea recibida y enviada al worker (sótano)",
        "task_id": task.id,
        "info": "Usa el ID para consultar el estado en /celery/status/{task_id}"
    }

@celery_router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Consulta el estado de una tarea en el backend de Celery (Redis).
    """
    # Obtenemos el resultado asíncrono usando el ID
    task_result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status, # Estados: PENDING, STARTED, SUCCESS, FAILURE
        "result": task_result.result  # El return de la función slow_task (si terminó)
    }