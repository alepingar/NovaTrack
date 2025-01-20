import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.schemas import settings  # Asegúrate de tener tus configuraciones cargadas

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