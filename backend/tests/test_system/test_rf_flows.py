
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from fastapi import HTTPException, UploadFile
from bson import ObjectId
from datetime import datetime, timezone, timedelta
import io
from app.main import app 
from app.utils.security import get_current_user 
from app.models.company import CompanyResponse, CompanyCreate, EntityType
from app.models.auth import Token 

import app.routes.company_routes as company_routes_module
import app.routes.auth_routes as auth_routes_module
import app.routes.transfer_routes as transfer_routes_module

# Cliente de prueba
client = TestClient(app)

# --- Datos y Funciones Auxiliares ---
fake_user_data = {"email": "system@test.com", "user_id": "user-sys", "company_id": "60d5ec49a5a0a2f9a4a5a6a7"}
fake_company_id_obj = ObjectId(fake_user_data["company_id"])

async def override_get_current_user():
    return fake_user_data

COMPANY_ROUTE_PREFIX = "/companies"
AUTH_ROUTE_PREFIX = "/auth"
TRANSFER_ROUTE_PREFIX = "/transfers"


# --- Pruebas Basadas en RFs ---

# RF-01: Registro de Nueva Empresa
def test_rf01_registro_nueva_empresa(mocker):
    """Simula el flujo RF-01 llamando al endpoint de registro."""

    company_data = {
    "name": "TestFinalReg", # Nuevo nombre para claridad
    "email": "final@test.com", # O el email correspondiente
    "password": "password123",
    "confirm_password": "password123",
    "country": "ES",
    "entity_type": EntityType.SL.value, # <-- Usar el VALOR ("Sociedad Limitada")
    "billing_account_number": "ES9121000418401234567891", # IBAN válido
    "terms_accepted": True,
    "privacy_policy_accepted": True,
    "data_processing_consent": True,

    "founded_date": datetime(2020, 1, 15).isoformat() # <-- Añadir fecha válida en formato ISO
    }
    # Datos simulados que devolvería el servicio si tuviera éxito
    mock_response_data = {
        "id": str(ObjectId()), "name": company_data["name"], "email": company_data["email"],
        "country": company_data["country"], "created_at": datetime.now(), "updated_at": datetime.now()
        # Añadir otros campos requeridos por CompanyResponse
    }

    # Mockear la función de servicio register_new_company llamada por la ruta
    mock_register_service = AsyncMock(return_value=CompanyResponse(**mock_response_data))
    mocker.patch.object(company_routes_module, 'register_new_company', mock_register_service)

    # Acción: Llamar al endpoint de registro
    response = client.post(f"{COMPANY_ROUTE_PREFIX}/register", json=company_data)

    # Aserciones: Verificar la respuesta HTTP y la llamada al servicio
    print(f"\n--- DETALLE ERROR 422 (Registro RF01) ---\n{response.json()}\n----------------------------------------\n")
    assert response.status_code == 200 # Asumiendo que el registro exitoso devuelve 200
    assert response.json()["email"] == company_data["email"]
    mock_register_service.assert_awaited_once() # Verificar que el servicio fue llamado


# RF-02: Inicio de Sesión (Éxito)
def test_rf02_inicio_sesion_exito(mocker):
    """Simula el flujo RF-02 (login exitoso) llamando al endpoint."""
    test_email = "rf02@test.com"
    test_password = "password_correcta"
    fake_token = "fake_jwt_for_rf02"

    # Mockear la función de servicio authenticate_user
    mock_auth_service = AsyncMock(return_value=fake_token)
    mocker.patch.object(auth_routes_module, 'authenticate_user', mock_auth_service)

    # Acción: Llamar al endpoint de login
    response = client.post(f"{AUTH_ROUTE_PREFIX}/login", json={"email": test_email, "password": test_password})

    # Aserciones
    
    assert response.status_code == 200
    assert response.json()["access_token"] == fake_token
    assert response.json()["token_type"] == "bearer"
    mock_auth_service.assert_awaited_once_with(test_email, test_password)


# RF-02: Inicio de Sesión (Fallo)
def test_rf02_inicio_sesion_fallo(mocker):
    """Simula el flujo RF-02 (login fallido) llamando al endpoint."""
    test_email = "rf02@test.com"
    test_password = "password_incorrecta"

    # Mockear servicio para que lance excepción 401
    mock_auth_service = AsyncMock(side_effect=HTTPException(status_code=401, detail="Credenciales inválidas"))
    mocker.patch.object(auth_routes_module, 'authenticate_user', mock_auth_service)

    # Acción: Llamar al endpoint de login
    response = client.post(f"{AUTH_ROUTE_PREFIX}/login", json={"email": test_email, "password": test_password})

    # Aserciones
    assert response.status_code == 401
    assert "Credenciales inválidas" in response.json()["detail"]
    mock_auth_service.assert_awaited_once_with(test_email, test_password)


@pytest.mark.asyncio
async def test_rf08_carga_camt_exito(mocker): # SIN self
    """Simula el flujo RF-08 (carga CAMT) llamando al endpoint."""
    mock_upload_response = {"message": "Archivo CAMT recibido y en proceso", "transfers_found": 50}
    mock_upload_service = AsyncMock(return_value=mock_upload_response)
    mocker.patch.object(transfer_routes_module, 'upload_camt_file', mock_upload_service)
    dummy_file_content = b"<camt>...Contenido Falso...</camt>"
    dummy_file = io.BytesIO(dummy_file_content)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.post(
        f"{TRANSFER_ROUTE_PREFIX}/upload-camt",
        files={"file": ("mi_fichero.xml", dummy_file, "application/xml")}
    )
    app.dependency_overrides = {}

    # Aserciones
    assert response.status_code == 200
    assert response.json() == mock_upload_response
    mock_upload_service.assert_awaited_once()
    call_args, _ = mock_upload_service.await_args
    assert call_args[1] == fake_user_data["company_id"] 

