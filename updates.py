from datetime import datetime
from uuid import uuid4,UUID
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

class Notification(BaseModel):
    message: str
    timestamp: datetime
    type: str
    company_id: str

# Conectar con MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
notifications_collection = db["notifications"]  # Cambié el nombre a "notifications"

async def insert_notification(message: str, notification_type: str, company_id: str):
    notification = Notification(
        message=message,
        timestamp=datetime.utcnow(),  # Usamos la hora actual en UTC
        type=notification_type,
        company_id=company_id
    )

    # Insertar la notificación en la base de datos
    result = await notifications_collection.insert_one(notification.dict())

# Ejecutar la inserción de notificación
asyncio.run(insert_notification("Nueva transferencia detectada", "Alerta", "678e8959a2f4f54c5d481ba1"))
