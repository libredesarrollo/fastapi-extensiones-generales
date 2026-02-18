from fastapi import APIRouter, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel

email_router = APIRouter()

# Configuración de la conexión SMTP
# ¡ADVERTENCIA! En producción, estas credenciales deben cargarse desde variables de entorno.
conf = ConnectionConfig(
    MAIL_USERNAME = "ec5cbede982042",
    MAIL_PASSWORD = "08243f07fb0be7",
    MAIL_FROM = "admin@admin.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "sandbox.smtp.mailtrap.io", # Por ejemplo, "smtp.gmail.com" para Gmail
    MAIL_SSL_TLS = False,
    MAIL_STARTTLS = False,
    # USE_CREDENTIALS = True,
    # VALIDATE_CERTS = True
)

class EmailSchema(BaseModel):
    recipient: EmailStr
    subject: str
    username: str

async def send_in_background(email_data: EmailSchema):
    # Definición del template HTML
    html_template = f"""
    <html>
        <body>
            <h1>Hola, {email_data.username}!</h1>
            <p>Gracias por unirte a nuestra plataforma.</p>
            <p>Este es un mensaje de prueba enviado desde <b>FastAPI</b>.</p>
            <br>
            <small>Si no solicitaste este correo, por favor ignóralo.</small>
        </body>
    </html>
    """

    message = MessageSchema(
        subject=email_data.subject,
        recipients=[email_data.recipient],
        body=html_template,
        subtype=MessageType.html # O MessageType.plain
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

@email_router.post("/send")
async def send_email_route(email_data: EmailSchema, background_tasks: BackgroundTasks):
    # El envío de correo se delega a una tarea en segundo plano para no bloquear la respuesta HTTP
    background_tasks.add_task(send_in_background, email_data)
    return {"message": "Email en proceso de envío."}