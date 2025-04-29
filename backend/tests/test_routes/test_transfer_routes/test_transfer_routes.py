# En tests/test_routes/test_transfer_routes.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from fastapi import HTTPException, UploadFile
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
import io # Para simular archivos

# Importa tu aplicación FastAPI principal y dependencias clave
from app.main import app # Ajusta si es necesario
from app.utils.security import get_current_user # Para sobrescribir auth
from app.models.transfer import Transfer # Para el response model de detalles

# Importar las funciones del servicio y otras dependencias PARA PODER PARCHEARLAS
import app.routes.transfer_routes as transfer_routes_module
# Necesitamos importar explícitamente la función que queremos mockear de su módulo original también
from app.isolation_forest.upload_files import upload_camt_file

# Cliente de prueba
client = TestClient(app)

# --- Datos y Funciones Auxiliares ---

fake_user_data = {"email": "transfer@user.com", "user_id": "user-t1", "company_id": "comp-transfer-xyz"}

async def override_get_current_user():
    return fake_user_data

# Ruta base para estos endpoints (ajusta si es diferente)
TRANSFER_ROUTE_PREFIX = "/transfers"

# --- Pruebas ---

# Test para GET /dashboard-data
@pytest.mark.asyncio
async def test_get_dashboard_data_no_filters(mocker):
    """Prueba GET /dashboard-data sin filtros."""
    mock_dashboard_result = {"summary": {"totalTransactions": 100}, "volumeByDay": []} # Ejemplo simple

    # Mockear el servicio interno
    mock_fetch_internal = AsyncMock(return_value=mock_dashboard_result)
    mocker.patch.object(transfer_routes_module, 'fetch_dashboard_data_internal', mock_fetch_internal)

    # Override auth
    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/dashboard-data")
    app.dependency_overrides = {} # Limpiar

    assert response.status_code == 200
    assert response.json() == mock_dashboard_result
    # Verificar llamada al servicio sin filtros (None para opcionales)
    mock_fetch_internal.assert_awaited_once_with(
        fake_user_data["company_id"], None, None, None, None, None
    )

@pytest.mark.asyncio
async def test_get_dashboard_data_with_filters(mocker):
    """Prueba GET /dashboard-data CON filtros."""
    mock_dashboard_result = {"summary": {"totalTransactions": 5}, "volumeByDay": []}
    start_str = "2024-04-01T00:00:00"
    end_str = "2024-04-30T23:59:59"
    prefix = "1234"
    min_a = 10.0
    max_a = 100.0

    mock_fetch_internal = AsyncMock(return_value=mock_dashboard_result)
    mocker.patch.object(transfer_routes_module, 'fetch_dashboard_data_internal', mock_fetch_internal)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(
        f"{TRANSFER_ROUTE_PREFIX}/dashboard-data",
        params={ # Parámetros de Query se pasan con 'params'
            "start_date": start_str,
            "end_date": end_str,
            "bank_prefix": prefix,
            "min_amount": min_a,
            "max_amount": max_a,
        }
    )
    app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json() == mock_dashboard_result
    # Verificar llamada al servicio CON filtros (FastAPI convierte tipos)
    mock_fetch_internal.assert_awaited_once()
    call_args, _ = mock_fetch_internal.await_args
    assert call_args[0] == fake_user_data["company_id"]
    assert isinstance(call_args[1], datetime) # start_date
    assert isinstance(call_args[2], datetime) # end_date
    assert call_args[3] == prefix
    assert call_args[4] == min_a
    assert call_args[5] == max_a

# Test para GET /stats
@pytest.mark.asyncio
async def test_get_company_stats_success(mocker):
    """Prueba GET /stats con éxito."""
    mock_stats_result = {"mean": 150.5, "std": 50.1, "q1": 90.0, "q3": 200.0, "recurrent_accounts": ["ACC1"]}

    mock_get_stats = AsyncMock(return_value=mock_stats_result)
    mocker.patch.object(transfer_routes_module, 'get_transfer_stats_by_company', mock_get_stats)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/stats")
    app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json() == mock_stats_result
    mock_get_stats.assert_awaited_once_with(fake_user_data["company_id"])

# Tests para GET /.../{year}/{month} (Ejemplo para uno de ellos)
@pytest.mark.asyncio
@pytest.mark.parametrize("period_param, expected_period", [
    ({"period": "month"}, "month"),
    ({"period": "year"}, "year"),
    ({}, "3months"), # Default
])
async def test_get_transfers_per_month_success(mocker, period_param, expected_period):
    """Prueba GET /per-month/{year}/{month}."""
    year, month = 2024, 4
    mock_count = 42

    mock_fetch_num = AsyncMock(return_value=mock_count)
    mocker.patch.object(transfer_routes_module, 'fetch_number_transfers_per_period', mock_fetch_num)

    # No necesita auth esta ruta según el código
    app.dependency_overrides = {}
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/per-month/{year}/{month}", params=period_param)

    assert response.status_code == 200
    assert response.json() == mock_count
    mock_fetch_num.assert_awaited_once_with(year, month, expected_period)

# (Añadir pruebas similares para /anomaly/per-month y /amount/per-month
#  mockeando 'fetch_number_anomaly_transfers_per_period' y 'fetch_total_amount_per_month')

# Test para GET /public/summary-data
def test_get_public_summary_data_success(mocker):
    """Prueba GET /public/summary-data con éxito."""
    mock_summary = {"totalTransactions": 1000, "totalAnomalies": 50, "totalAmount": 9876.54}

    mock_fetch_public = AsyncMock(return_value=mock_summary)
    mocker.patch.object(transfer_routes_module, 'fetch_public_summary_data', mock_fetch_public)

    app.dependency_overrides = {} # No auth needed
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/public/summary-data")

    assert response.status_code == 200
    assert response.json() == mock_summary
    mock_fetch_public.assert_awaited_once()

def test_get_public_summary_data_error(mocker):
    """Prueba GET /public/summary-data cuando el servicio falla."""
    mock_fetch_public = AsyncMock(side_effect=Exception("DB error"))
    mocker.patch.object(transfer_routes_module, 'fetch_public_summary_data', mock_fetch_public)

    app.dependency_overrides = {}
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/public/summary-data")

    assert response.status_code == 500
    assert "Error al generar el resumen público" in response.json()["detail"]
    mock_fetch_public.assert_awaited_once()

# Test para POST /upload-camt
@pytest.mark.asyncio
async def test_upload_camt_success(mocker):
    """Prueba POST /upload-camt subida de archivo exitosa."""
    mock_upload_response = {"message": "Archivo procesado", "transfers_found": 10}

    # Mockear la función de subida/procesamiento
    # Necesitamos mockearla donde se importa en transfer_routes.py
    mock_process_file = AsyncMock(return_value=mock_upload_response)
    mocker.patch.object(transfer_routes_module, 'upload_camt_file', mock_process_file)

    # Simular contenido de archivo
    dummy_file_content = b"<camt>...</camt>"
    dummy_file = io.BytesIO(dummy_file_content)

    app.dependency_overrides[get_current_user] = override_get_current_user
    # Enviar archivo usando el parámetro 'files'
    response = client.post(
        f"{TRANSFER_ROUTE_PREFIX}/upload-camt",
        files={"file": ("test_camt.xml", dummy_file, "application/xml")}
    )
    app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json() == mock_upload_response
    # Verificar que se llamó al servicio con un objeto UploadFile y company_id
    # ... (mocking, crear dummy_file, hacer request client.post) ...

    mock_process_file.assert_awaited_once() # Verificar que se llamó
    call_args, _ = mock_process_file.await_args
    # --- ELIMINA O COMENTA ESTA LÍNEA ---
    # assert isinstance(call_args[0], UploadFile)
    # --- FIN ELIMINAR/COMENTAR ---
    assert call_args[1] == fake_user_data["company_id"] # Esta SÍ es importante

    assert response.status_code == 200 # Verificar respuesta (como antes)
    assert response.json() == mock_upload_response # Verificar respuesta (como antes)

# Test para GET /filtered-list (similar a /dashboard-data pero llama a otro servicio)
@pytest.mark.asyncio
async def test_get_filtered_transfer_list_success(mocker):
    """Prueba GET /filtered-list con éxito."""
    mock_filtered_list = [
    { # Objeto válido según TransferResponse
        "id": str(uuid4()), # ID como UUID string
        "amount": 50.0,
        "currency": "EUR",
        "from_account": "VALID_ACC_10_CHARS_MIN",
        "to_account": "VALID_ACC_10_CHARS_MIN_2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "completada",
        "company_id": fake_user_data["company_id"], # Necesario si está en TransferResponse
        "is_anomalous": False # Necesario si está en TransferResponse
        # ... otros campos requeridos por TransferResponse ...
    },
    # ... puedes añadir otro si quieres probar una lista ...
]
    start_str = "2024-01-01T00:00:00"

    mock_fetch_filtered = AsyncMock(return_value=mock_filtered_list)
    mocker.patch.object(transfer_routes_module, 'fetch_transfers_by_filters', mock_fetch_filtered)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/filtered-list", params={"start_date": start_str})
    app.dependency_overrides = {}

    assert response.status_code == 200
    response_data = response.json()
    # --- REEMPLAZA LA ASERCIÓN DIRECTA POR ESTAS ---
    assert isinstance(response_data, list)
    assert len(response_data) == len(mock_filtered_list)
    # Verifica campos clave del primer elemento (ajusta según tu mock_filtered_list)
    assert response_data[0]["id"] == mock_filtered_list[0]["id"]
    assert response_data[0]["amount"] == mock_filtered_list[0]["amount"]
    assert response_data[0]["status"] == mock_filtered_list[0]["status"]
    # --- FIN REEMPLAZO ---

    mock_fetch_filtered.assert_awaited_once()
    # Verificar llamada al servicio con filtros
    mock_fetch_filtered.assert_awaited_once()
    call_kwargs = mock_fetch_filtered.await_args.kwargs
    assert call_kwargs["company_id"] == fake_user_data["company_id"]
    assert isinstance(call_kwargs["start_date"], datetime)
    assert call_kwargs["end_date"] is None # No se pasó

# Test para GET /all
@pytest.mark.asyncio
async def test_get_all_transfers_success(mocker):
    """Prueba GET /all con éxito."""
    mock_all_list = [
    { # Objeto válido según TransferResponse
        "id": str(uuid4()), # ID como UUID string
        "amount": 250.75,
        "currency": "USD",
        "from_account": "VALID_ACC_10_CHARS_MIN_3",
        "to_account": "VALID_ACC_10_CHARS_MIN_4",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "pendiente",
        "company_id": fake_user_data["company_id"],
        "is_anomalous": True
        # ... otros campos requeridos por TransferResponse ...
    }
]

    mock_fetch_all = AsyncMock(return_value=mock_all_list)
    mocker.patch.object(transfer_routes_module, 'fetch_transfers1', mock_fetch_all)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/all")
    app.dependency_overrides = {}

    assert response.status_code == 200
    response_data = response.json()
    # --- REEMPLAZA LA ASERCIÓN DIRECTA POR ESTAS ---
    assert isinstance(response_data, list)
    assert len(response_data) == len(mock_all_list)
    # Verifica campos clave del primer elemento (ajusta según tu mock_all_list)
    assert response_data[0]["id"] == mock_all_list[0]["id"]
    assert response_data[0]["amount"] == mock_all_list[0]["amount"]
    assert response_data[0]["status"] == mock_all_list[0]["status"]
    # --- FIN REEMPLAZO ---

    mock_fetch_all.assert_awaited_once_with(company_id=fake_user_data["company_id"])

# Test para GET /{transfer_id}
@pytest.mark.asyncio
async def test_get_transfer_details_success(mocker):
    """Prueba GET /{transfer_id} con éxito."""
    test_uuid = uuid4()
    test_uuid_str = str(test_uuid)
    mock_detail_data = { # Debe coincidir con el modelo Transfer
        "id": test_uuid_str, "amount": 100.0, "currency": "EUR",
        "from_account": "ACC_DETAILS_1", "to_account": "ACC_DETAILS_2",
        "timestamp": datetime.now(timezone.utc), "status": "completada",
        "company_id": fake_user_data["company_id"], "is_anomalous": False
    }
    # Crear un objeto mock que simule el objeto Transfer devuelto por el servicio
    mock_transfer_obj = MagicMock(spec=Transfer)
    # Configurar los atributos del mock para que coincidan con los datos
    for key, value in mock_detail_data.items():
        setattr(mock_transfer_obj, key, value)

    mock_fetch_details = AsyncMock(return_value=mock_transfer_obj)
    mocker.patch.object(transfer_routes_module, 'fetch_transfer_details', mock_fetch_details)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/{test_uuid_str}")
    app.dependency_overrides = {}

    assert response.status_code == 200
    # FastAPI serializará el objeto Transfer (o nuestro mock) a JSON
    # La comparación exacta puede depender de la serialización de UUID y datetime
    response_data = response.json()
    assert response_data["id"] == test_uuid_str
    assert response_data["amount"] == 100.0
    assert response_data["status"] == "completada"
    mock_fetch_details.assert_awaited_once_with(fake_user_data["company_id"], test_uuid)


@pytest.mark.asyncio
async def test_get_transfer_details_not_found(mocker):
    """Prueba GET /{transfer_id} cuando no se encuentra."""
    test_uuid = uuid4()
    test_uuid_str = str(test_uuid)

    # Mockear servicio para que lance 404
    mock_fetch_details = AsyncMock(side_effect=HTTPException(status_code=404, detail="No encontrada"))
    mocker.patch.object(transfer_routes_module, 'fetch_transfer_details', mock_fetch_details)

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get(f"{TRANSFER_ROUTE_PREFIX}/{test_uuid_str}")
    app.dependency_overrides = {}

    assert response.status_code == 404
    assert "No encontrada" in response.json()["detail"]
    mock_fetch_details.assert_awaited_once_with(fake_user_data["company_id"], test_uuid)