# auth_services.py
from app.utils.security import hash_password, verify_password, create_access_token
from app.database import db
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.auth import settings  # Asegúrate de tener tus configuraciones cargadas


async def authenticate_user(email: str, password: str):
    """
    Authenticate a user (company or individual) by email and password.
    """
    # Buscar en empresas
    company = await db.companies.find_one({"email": email})
    if company and verify_password(password, company["password"]):
        return create_access_token(data={
            "sub": company["email"],
            "role": "admin",
            "company_id": str(company["_id"])
        })

    raise HTTPException(status_code=401, detail="Credenciales inválidas")


def send_email(to_email: str, subject: str, content: str):
    try:
        # Crear el mensaje
        message = MIMEMultipart()
        message["From"] = f"{settings.email_name} <{settings.email_from}>"
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(content, "html"))

        # Configurar conexión SMTP
        with smtplib.SMTP(settings.email_host, settings.email_port) as server:
            server.starttls()
            server.login(settings.email_user, settings.email_password)
            server.sendmail(settings.email_from, to_email, message.as_string())

        print(f"Correo enviado a {to_email}")
    except Exception as e:
        print(f"Error enviando correo: {e}")

async def generate_reset_token(email: str):
    """
    Generate a password reset token and send email.
    """
    user = await db.companies.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Correo no registrado")

    # Crear un token de recuperación (ejemplo: simple hash)
    reset_token = "TOKEN_GENERADO_AQUI"

    # Guardar el token en la base de datos (opcional)
    await db.companies.update_one({"email": email}, {"$set": {"reset_token": reset_token}})

    # Crear enlace de recuperación
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

    # Enviar el correo
    subject = "Recupera tu contraseña"
    content = f"""
    <h1>Recupera tu contraseña</h1>
    <p>Haz clic en el enlace para restablecer tu contraseña:</p>
    <a href="{reset_link}">{reset_link}</a>
    """
    send_email(email, subject, content)

    return {"message": "Correo de recuperación enviado"}


async def reset_user_password(token: str, new_password: str):
    """
    Reset the user's password using a valid token.
    """
    user = await db.companies.find_one({"reset_token": token})
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    # Actualizar contraseña
    hashed_password = hash_password(new_password)
    await db.companies.update_one({"reset_token": token}, {
        "$set": {"password": hashed_password},
        "$unset": {"reset_token": ""},
    })

    return {"message": "Contraseña restablecida correctamente"}




