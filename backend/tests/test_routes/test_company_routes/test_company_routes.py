# En tests/test_routes/test_company_routes.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from freezegun import freeze_time

# Importa tu aplicación FastAPI principal y dependencias clave
from app.main import app # Ajusta si es necesario
from app.utils.security import get_current_user # Para sobrescribir auth
from app.models.company import ( # Importar modelos usados en request/response
    CompanyResponse, CompanyCreate, UpdateCompanyProfile,
    EntityType, SubscriptionPlan, CompanyGDPRRequest, ConsentUpdate
)
# Importar las funciones/clases del servicio PARA PODER PARCHEARLAS donde se usan
import app.routes.company_routes as company_routes_module
# Importar ObjectId para usarlo en mocks y aserciones
from bson import ObjectId


# Cliente de prueba
client = TestClient(app)

# --- Datos y Funciones Auxiliares ---
fake_user_data = {"email": "company@user.com", "user_id": "user-c1", "company_id": "60d5ec49a5a0a2f9a4a5a6a7"} # Usar un ID válido como string
fake_company_id_obj = ObjectId(fake_user_data["company_id"])

async def override_get_current_user():
    return fake_user_data

# Ruta base para estos endpoints (ajusta si es diferente)
COMPANY_ROUTE_PREFIX = "/companies"

# --- Pruebas ---

@pytest.mark.asyncio # Añadido async si la función de servicio lo es
async def test_get_companies_success(mocker): # Añadido self
    mock_now = datetime.now(timezone.utc)
    # Datos base VÁLIDOS según CompanyResponse
    mock_company_data_list = [
        {
            "id": "comp1", "name": "Comp A", "email": "a@c.com", "industry": "Tech",
            "country": "ES", "created_at": mock_now, "updated_at": mock_now,
            "phone_number": None, "tax_id": None, "address": None, "founded_date": None,
            "billing_account_number": None, "subscription_plan": None
        },
        {
            "id": "comp2", "name": "Comp B", "email": "b@c.com", "industry": "Finance",
            "country": "UK", "created_at": mock_now, "updated_at": mock_now,
            "phone_number": None, "tax_id": None, "address": None, "founded_date": None,
            "billing_account_number": None, "subscription_plan": None
        }
    ]
    # Crear instancias Pydantic para el mock return_value
    mock_response_objects = [CompanyResponse(**d) for d in mock_company_data_list]

    mock_fetch = AsyncMock(return_value=mock_response_objects)
    mocker.patch.object(company_routes_module, 'fetch_companies', mock_fetch)

    response = client.get(f"{COMPANY_ROUTE_PREFIX}/")

    # Verificaciones
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 2
    # Compara campos clave individuales con mock_company_data_list
    assert response_data[0]['id'] == mock_company_data_list[0]['id']
    assert response_data[0]['name'] == mock_company_data_list[0]['name']
    assert response_data[0]['country'] == mock_company_data_list[0]['country']
    assert "address" in response_data[0] # Verificar existencia de opcionales
    assert isinstance(response_data[0]['created_at'], str) # Verificar tipo fecha
    datetime.fromisoformat(response_data[0]['created_at']) # Verificar formato fecha
    mock_fetch.assert_awaited_once()

# Test para GET /profile
@pytest.mark.asyncio
async def test_get_company_profile_success(mocker):
    """Prueba GET /profile con éxito."""
    mock_profile_data = {"id": fake_user_data["company_id"], "name": "My Profile Co", "email": "company@user.com", "country": "ES", "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()}

    mock_fetch_profile = AsyncMock(return_value=CompanyResponse(**mock_profile_data))
    mocker.patch.object(company_routes_module, 'fetch_company_profile', mock_fetch_profile)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(f"{COMPANY_ROUTE_PREFIX}/profile")
    app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json()["id"] == fake_user_data["company_id"]
    assert response.json()["name"] == mock_profile_data["name"]
    mock_fetch_profile.assert_awaited_once_with(fake_user_data["company_id"])

# Test para GET /get-types
def test_get_entity_types_success(mocker):
    """Prueba GET /get-types."""
    mock_types = ["Sociedad Anónima", "Sociedad Limitada"] # Ejemplo
    # Mockear el servicio get_entity_types1
    mock_get = AsyncMock(return_value=[EntityType(t) for t in mock_types]) # Devolver Enum members
    mocker.patch.object(company_routes_module, 'get_entity_types1', mock_get)

    response = client.get(f"{COMPANY_ROUTE_PREFIX}/get-types")

    assert response.status_code == 200
    assert response.json() == mock_types # FastAPI convierte Enums a sus valores (strings)
    mock_get.assert_awaited_once()

# Test para POST /upgrade-plan
def test_upgrade_plan_success(mocker):
    """Prueba POST /upgrade-plan."""
    expected_url = "https://checkout.stripe.com/pay/cs_test_..."
    # Mockear el método estático del servicio StripeService
    mock_create_session = mocker.patch.object(company_routes_module.StripeService, 'create_checkout_session', return_value=expected_url)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.post(f"{COMPANY_ROUTE_PREFIX}/upgrade-plan")
    app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json() == {"checkoutUrl": expected_url}
    mock_create_session.assert_called_once_with(fake_company_id_obj) # Verifica que se llame con ObjectId

# Test para POST /confirm-plan
@pytest.mark.asyncio
async def test_confirm_plan_success(mocker):
    """Prueba POST /confirm-plan."""
    mock_confirm_response = {"status": "success", "message": "Plan OK", "expires_at": datetime.now()}
    mock_confirm = AsyncMock(return_value=mock_confirm_response)
    mocker.patch.object(company_routes_module, 'confirmar_pago', mock_confirm)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.post(f"{COMPANY_ROUTE_PREFIX}/confirm-plan")
    app.dependency_overrides = {}

    assert response.status_code == 200
    # El datetime se serializará, compara los otros campos
    assert response.json()["status"] == mock_confirm_response["status"]
    assert response.json()["message"] == mock_confirm_response["message"]
    mock_confirm.assert_awaited_once_with(fake_company_id_obj) # Verifica que se llame con ObjectId

# Test para GET /get-current-plan
@pytest.mark.asyncio
async def test_get_plan_success(mocker):
    """Prueba GET /get-current-plan."""
    mock_plan = SubscriptionPlan.PRO # Devolver el Enum member

    mock_get_plan = AsyncMock(return_value=mock_plan)
    mocker.patch.object(company_routes_module, 'get_current_plan', mock_get_plan)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(f"{COMPANY_ROUTE_PREFIX}/get-current-plan")
    app.dependency_overrides = {}

    assert response.status_code == 200
    # FastAPI serializa el Enum a su valor (string)
    assert response.json() == mock_plan.value
    mock_get_plan.assert_awaited_once_with(fake_user_data["company_id"])

# Tests para GDPR/Consent/Deletion (Ejemplo para uno de ellos)
@pytest.mark.asyncio
async def test_gdpr_request_success(mocker):
    """Prueba POST /gdpr/request."""
    action_input = {"action": "access"}
    mock_service = AsyncMock() # No devuelve nada relevante
    mocker.patch.object(company_routes_module, 'request_gdpr_action', mock_service)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.post(f"{COMPANY_ROUTE_PREFIX}/gdpr/request", json=action_input)
    app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json() == {"message": f"Solicitud GDPR '{action_input['action']}' registrada correctamente"}
    mock_service.assert_awaited_once_with(fake_user_data["company_id"], action_input['action'])
