
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app 
from app.utils.security import get_current_user 

import app.routes.notification_routes as notification_routes_module

# Cliente de prueba
client = TestClient(app)

# --- Datos y Funciones Auxiliares para Pruebas ---

# Un usuario simulado que devolverá nuestra dependencia de seguridad mockeada
fake_user_data = {"email": "test@user.com", "user_id": "user-123", "company_id": "comp-abc-987"}

# Función que usaremos para sobrescribir get_current_user
async def override_get_current_user():
    return fake_user_data

# --- Pruebas ---

def test_get_notifications_success(mocker):
    """Prueba GET /notifications (o la ruta base) con éxito."""
    # Datos simulados que devolverá el servicio mockeado
    mock_notifications_list = [
        {"id": "notif_1", "message": "Mensaje 1", "type": "info"},
        {"id": "notif_2", "message": "Mensaje 2", "type": "warning"},
    ]

    # Mockear la función del servicio fetch_notifications
    mock_fetch = AsyncMock(return_value=mock_notifications_list)
    mocker.patch.object(notification_routes_module, 'fetch_notifications', mock_fetch)
    # Nota: Usamos patch.object porque importamos el módulo entero

    # Sobrescribir la dependencia de autenticación
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Realizar la petición GET (Ajusta la ruta si tiene prefijo)
    response = client.get("/notifications/") # Asume que el router se montó en /notifications

    # Limpiar la sobrescritura de dependencia DESPUÉS de la petición
    app.dependency_overrides = {}

    # Verificaciones
    assert response.status_code == 200
    assert response.json() == mock_notifications_list
    # Verificar que se llamó al servicio con el company_id del usuario mockeado
    mock_fetch.assert_awaited_once_with(fake_user_data["company_id"])

def test_delete_notification_success(mocker):
    """Prueba DELETE /notifications/{notification_id} con éxito."""
    test_notification_id = "notif_to_delete_123"

    # Mockear la función del servicio delete_notification
    mock_delete = AsyncMock() # No necesita devolver nada
    mocker.patch.object(notification_routes_module, 'delete_notification', mock_delete)

    # Sobrescribir la dependencia de autenticación
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Realizar la petición DELETE (Ajusta la ruta si tiene prefijo)
    response = client.delete(f"/notifications/{test_notification_id}")

    # Limpiar la sobrescritura
    app.dependency_overrides = {}

    # Verificaciones
    assert response.status_code == 200
    assert response.json() == {"message": "Notificación eliminada"}
    # Verificar que se llamó al servicio con el ID de notificación y el company_id correctos
    mock_delete.assert_awaited_once_with(test_notification_id, fake_user_data["company_id"])

def test_get_notifications_unauthenticated():
    """Prueba GET /notifications sin autenticación (sin token/override)."""
    # Asegurarse de que no hay overrides activos
    app.dependency_overrides = {}

    # Realizar la petición SIN cabecera de autorización implícita
    response = client.get("/notifications/")

    # Verificar que falla con 401 Unauthorized (o el código que devuelva tu get_current_user real)
    assert response.status_code == 401
    # assert response.json()["detail"] == "Not authenticated" o similar

