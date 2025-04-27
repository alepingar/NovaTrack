# En tests/test_services/test_notification_service.py

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, ANY
from bson import ObjectId

from app.services.notification_services import save_notification, NOTIFICATION_TTL_DAYS

MODULE_PATH = "app.services.notification_services"

@pytest.mark.asyncio
async def test_save_notification_inserts_correct_data(mocker):
    """
    Prueba que save_notification llama a insert_one con los datos correctos.
    """
    test_message = "¡Nueva Alerta!"
    test_type = "alerta"
    test_company_id = "comp_123" 

    mock_notifications_collection = AsyncMock()

    mock_notifications_collection.insert_one = AsyncMock()

    mocker.patch(f"{MODULE_PATH}.db.notifications", mock_notifications_collection)

    # Llamar a la función bajo prueba
    await save_notification(test_message, test_type, test_company_id)

    # Verificar que el mock fue llamado correctamente
    mock_notifications_collection.insert_one.assert_called_once()

    expected_data_structure = {
        "message": test_message,
        "timestamp": ANY,
        "type": test_type,
        "company_id": test_company_id,
        "expires_at": ANY
    }
    call_args, call_kwargs = mock_notifications_collection.insert_one.call_args
    actual_data = call_args[0]

    assert actual_data["message"] == expected_data_structure["message"]
    assert actual_data["type"] == expected_data_structure["type"]
    assert actual_data["company_id"] == expected_data_structure["company_id"]
    assert isinstance(actual_data["timestamp"], datetime)
    assert isinstance(actual_data["expires_at"], datetime)

    now = datetime.utcnow()
    expected_expiration = now + timedelta(days=NOTIFICATION_TTL_DAYS)
    assert abs(actual_data["expires_at"] - expected_expiration) < timedelta(seconds=10)
    assert abs(actual_data["timestamp"] - now) < timedelta(seconds=10)