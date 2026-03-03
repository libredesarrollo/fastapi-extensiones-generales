import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, HTMLResponse

streaming_router = APIRouter()

@streaming_router.get("/export-progress")
async def export_with_progress():
    """
    Endpoint SSE (Server-Sent Events) que simula una tarea larga (exportación)
    y envía actualizaciones de progreso al cliente en tiempo real.

    - **UX de Alta Calidad**: Permite al frontend mostrar una barra de progreso real.
    - **Eficiencia**: Usa una sola conexión HTTP unidireccional, más ligero que WebSockets.
    - **Anti-Timeouts**: Mantiene la conexión viva enviando datos constantemente.
    """
    
    async def progress_generator():
        # 1. Configuración de la simulación
        # En un escenario real, aquí obtendrías el total de registros de tu DB (SQLAlchemy, MongoDB, etc.)
        total_tasks = 20 
        
        if total_tasks == 0:
            yield "data: {\"progress\": 100, \"message\": \"No hay tareas para exportar\"}\n\n"
            return

        # Simulamos iterar sobre un cursor de base de datos
        for i in range(total_tasks):
            count = i + 1
            
            # Simulamos un pequeño retraso (trabajo pesado en el servidor)
            await asyncio.sleep(0.5) 
            
            # 2. Calculamos el porcentaje de avance
            percentage = int((count / total_tasks) * 100)
            
            # 3. Preparamos el payload con datos útiles para el usuario
            payload = {
                "progress": percentage,
                "task_name": f"Procesando registro #{count}",
                "status": "procesando"
            }
            
            # 4. Formato SSE: Siempre debe empezar con "data: " y terminar con "\n\n"
            # Esto permite al navegador distinguir cada evento individualmente.
            yield f"data: {json.dumps(payload)}\n\n"

        # Evento final para indicar que el proceso terminó
        final_payload = {"progress": 100, "status": "completado", "message": "Exportación finalizada"}
        yield f"data: {json.dumps(final_payload)}\n\n"

    # 5. El media_type "text/event-stream" es crucial: le dice al navegador 
    # que no cierre la conexión y espere un flujo de eventos.
    return StreamingResponse(progress_generator(), media_type="text/event-stream")

@streaming_router.get("/ui", response_class=HTMLResponse)
async def export_ui():
    """
    Endpoint que sirve una página HTML simple para visualizar el progreso SSE.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Progreso de Exportación</h1>
        <div id="status">Esperando...</div>
        
        <div style="width: 100%; background: #eee;">
            <div id="progress-bar" style="width: 0%; height: 20px; background: green; transition: width 0.3s;"></div>
        </div>

        <script>
            // 1. Conectamos al endpoint de FastAPI
            // Nota: La URL es /stream/export-progress porque el router tiene el prefijo /stream
            const eventSource = new EventSource("/stream/export-progress");

            // 2. Escuchamos los mensajes que llegan
            eventSource.onmessage = (event) => {
                // Parseamos el JSON que enviamos desde Python
                const data = JSON.parse(event.data);
                
                // Actualizamos la UI
                document.getElementById("status").innerText = `Procesando: ${data.task_name || '...'}`;
                document.getElementById("progress-bar").style.width = data.progress + "%";

                // 3. Si llega al 100%, cerramos la conexión
                if (data.progress === 100) {
                    document.getElementById("status").innerText = "¡Exportación Completada!";
                    eventSource.close(); 
                }
            };

            // Manejo de errores
            eventSource.onerror = (error) => {
                console.error("Error en el stream:", error);
                eventSource.close();
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)