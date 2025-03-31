from datetime import datetime, timedelta
from app.models.notification import Notification
from app.database import db
from bson import ObjectId

NOTIFICATION_TTL_DAYS = 7

async def save_notification(message: str, notification_type: str, company_id: str):
    expiration_time = datetime.utcnow() + timedelta(days=NOTIFICATION_TTL_DAYS)
    
    notification = {
        "message": message,
        "timestamp": datetime.utcnow(),
        "type": notification_type,
        "company_id": company_id,
        "expires_at": expiration_time
    }   
    await db.notifications.insert_one(notification)


async def fetch_notifications(company_id: str):
    notifications = await db.notifications.find({"company_id": company_id}).to_list(None)

    notifications = [
        {**notif, "_id": str(notif["_id"])} for notif in notifications
    ]
    return notifications


async def delete_notification(notification_id: str, company_id: str):
    """Eliminar notificación por ID"""
    try:
        notification_id = ObjectId(notification_id)
    except Exception as e:
        print(f"Error al convertir ID de notificación: {e}")
        return

    result = await db.notifications.delete_one({"_id": notification_id, "company_id": company_id})
    if result.deleted_count == 0:
        print("No se eliminó ninguna notificación.")
    else:
        print("Notificación eliminada correctamente.")




    