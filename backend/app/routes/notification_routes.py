from fastapi import APIRouter, Depends
from app.services.notification_services import fetch_notifications, delete_notification
from app.utils.security import get_current_user
router = APIRouter()



@router.get("/")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    """Obtiene todas las notificaciones de la empresa."""
    notifications = await fetch_notifications(current_user["company_id"])
    return notifications

@router.delete("/{notification_id}")
async def delete_notification_by_id(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Eliminar una notificación por su ID"""
    await delete_notification(notification_id, current_user["company_id"])
    return {"message": "Notificación eliminada"}