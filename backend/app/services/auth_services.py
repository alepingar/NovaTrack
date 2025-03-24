# auth_services.py
from datetime import datetime, timedelta
import secrets
from app.utils.security import hash_password, verify_password, create_access_token
from app.database import db
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.auth import settings

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=15) 

async def authenticate_user(email: str, password: str):
    """
    Autentica a una empresa por email y contraseña, y maneja seguridad.
    """
    company = await db.companies.find_one({"email": email})
    
    if not company:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Verificar si la cuenta está bloqueada
    if company.get("account_locked"):
        lock_time = company.get("lockout_until")
        if lock_time and datetime.utcnow() < lock_time:
            raise HTTPException(status_code=403, detail="Cuenta bloqueada por múltiples intentos fallidos. Intente más tarde.")
        else:
            # Desbloquear automáticamente si ha pasado el tiempo
            await db.companies.update_one({"email": email}, {"$set": {"account_locked": False, "failed_login_attempts": 0}})
    
    # Verificar la contraseña
    if not verify_password(password, company["password"]):
        failed_attempts = company.get("failed_login_attempts", 0) + 1
        update_data = {"failed_login_attempts": failed_attempts}
        
        # Bloquear la cuenta si supera el límite
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            update_data.update({
                "account_locked": True,
                "lockout_until": datetime.utcnow() + LOCKOUT_TIME
            })
        
        await db.companies.update_one({"email": email}, {"$set": update_data})
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Si la autenticación es correcta, resetear intentos fallidos y registrar el login
    await db.companies.update_one({"email": email}, {"$set": {
        "failed_login_attempts": 0,
        "account_locked": False,
        "last_login": datetime.utcnow()
    }})
    
    return create_access_token(data={
        "sub": company["email"],
        "company_id": str(company["_id"])
    })



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
    Generate a secure password reset token and send email.
    """
    user = await db.companies.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Este correo no existe")  # Mensaje actualizado

    # Generar un token seguro
    reset_token = secrets.token_urlsafe(32)

    # Guardar el token en la base de datos con tiempo de expiración
    await db.companies.update_one({"email": email}, {
        "$set": {
            "reset_token": reset_token,
            "reset_token_expiration": datetime.utcnow() + timedelta(hours=1)  # Expira en 1 hora
        }
    })

    # Crear enlace de recuperación
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

    # Enviar correo
    subject = "Recupera tu contraseña"
    content = f"""
    <h1>Recupera tu contraseña</h1>
    <p>Haz clic en el enlace para restablecer tu contraseña:</p>
    <a href="{reset_link}">{reset_link}</a>
    """
    send_email(email, subject, content)

    return send_email(email, subject, content)



async def reset_user_password(token: str, new_password: str):
    """
    Reset the user's password using a valid token.
    """
    user = await db.companies.find_one({"reset_token": token})
    if not user or "reset_token_expiration" not in user:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    # Verificar si el token ha expirado
    if datetime.utcnow() > user["reset_token_expiration"]:
        raise HTTPException(status_code=400, detail="El token ha expirado")

    # Actualizar contraseña
    hashed_password = hash_password(new_password)
    await db.companies.update_one({"reset_token": token}, {
        "$set": {"password": hashed_password},
        "$unset": {"reset_token": "", "reset_token_expiration": ""},
    })

    return {"message": "Contraseña restablecida correctamente"}



async def check_email(email: str):
    """
    Check if the email exists in the database.
    """
    user = await db.companies.find_one({"email": email})
    return bool(user)




