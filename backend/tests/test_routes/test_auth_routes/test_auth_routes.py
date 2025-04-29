
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.main import app

import app.routes.auth_routes as auth_routes_module

# Cliente de prueba
client = TestClient(app)

AUTH_ROUTE_PREFIX = "/auth"

# --- Pruebas para POST /login ---

def test_login_success(mocker):
    """Prueba login exitoso."""
    test_email = "test@example.com"
    test_password = "password123"
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.FakeTokenSignature"

    # Mockear el servicio authenticate_user
    mock_auth = AsyncMock(return_value=fake_token)
    mocker.patch.object(auth_routes_module, 'authenticate_user', mock_auth)

    # Realizar petición POST
    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/login",
        json={"email": test_email, "password": test_password}
    )

    # Verificaciones
    assert response.status_code == 200
    assert response.json() == {"access_token": fake_token, "token_type": "bearer"}
    mock_auth.assert_awaited_once_with(test_email, test_password)

def test_login_invalid_credentials(mocker):
    """Prueba login con credenciales inválidas (HTTPException desde servicio)."""
    test_email = "test@example.com"
    test_password = "wrongpassword"

    # Mockear authenticate_user para que lance HTTPException 401
    mock_auth = AsyncMock(side_effect=HTTPException(status_code=401, detail="Credenciales inválidas"))
    mocker.patch.object(auth_routes_module, 'authenticate_user', mock_auth)

    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/login",
        json={"email": test_email, "password": test_password}
    )

    # Verificaciones
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"
    mock_auth.assert_awaited_once_with(test_email, test_password)

def test_login_validation_error():
    """Prueba login con datos inválidos (error de validación Pydantic/FastAPI)."""
    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/login",
        json={"email": "not-an-email", "password": "pw"} # Email inválido
    )
    # FastAPI devuelve 422 para errores de validación Pydantic
    assert response.status_code == 422


# --- Pruebas para POST /reset-password ---

def test_reset_password_request_success(mocker):
    """Prueba solicitud de reseteo de contraseña exitosa."""
    test_email = "reset@example.com"
    expected_service_response = {"message": "Correo de recuperación enviado correctamente."}

    # Mockear generate_reset_token
    mock_generate = AsyncMock(return_value=expected_service_response)
    mocker.patch.object(auth_routes_module, 'generate_reset_token', mock_generate)

    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/reset-password",
        json={"email": test_email}
    )

    assert response.status_code == 200
    assert response.json() == expected_service_response
    mock_generate.assert_awaited_once_with(test_email)

def test_reset_password_request_user_not_found(mocker):
    """Prueba solicitud de reseteo para email no existente."""
    test_email = "notfound@example.com"

    # Mockear generate_reset_token para que lance HTTPException 404
    mock_generate = AsyncMock(side_effect=HTTPException(status_code=404, detail="Este correo no existe"))
    mocker.patch.object(auth_routes_module, 'generate_reset_token', mock_generate)

    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/reset-password",
        json={"email": test_email}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Este correo no existe"
    mock_generate.assert_awaited_once_with(test_email)

def test_reset_password_request_validation_error():
    """Prueba solicitud de reseteo con email inválido."""
    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/reset-password",
        json={"email": "not-an-email"}
    )
    assert response.status_code == 422


# --- Pruebas para POST /reset-password-confirm ---

def test_reset_password_confirm_success(mocker):
    """Prueba confirmación de reseteo de contraseña exitosa."""
    test_token = "valid_reset_token"
    test_password = "newStrongPassword123"
    expected_service_response = {"message": "Contraseña restablecida correctamente"}

    # Mockear reset_user_password
    mock_reset = AsyncMock(return_value=expected_service_response)
    mocker.patch.object(auth_routes_module, 'reset_user_password', mock_reset)

    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/reset-password-confirm",
        json={"token": test_token, "password": test_password}
    )

    assert response.status_code == 200
    assert response.json() == expected_service_response
    mock_reset.assert_awaited_once_with(test_token, test_password)

def test_reset_password_confirm_invalid_token(mocker):
    """Prueba confirmación de reseteo con token inválido/expirado."""
    test_token = "invalid_or_expired_token"
    test_password = "newStrongPassword123"

    # Mockear reset_user_password para que lance HTTPException 400
    mock_reset = AsyncMock(side_effect=HTTPException(status_code=400, detail="Token inválido o expirado"))
    mocker.patch.object(auth_routes_module, 'reset_user_password', mock_reset)

    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/reset-password-confirm",
        json={"token": test_token, "password": test_password}
    )

    assert response.status_code == 400
    assert "Token inválido o expirado" in response.json()["detail"]
    mock_reset.assert_awaited_once_with(test_token, test_password)

def test_reset_password_confirm_validation_error():
    """Prueba confirmación de reseteo con datos faltantes."""
    response = client.post(
        f"{AUTH_ROUTE_PREFIX}/reset-password-confirm",
        json={"token": "some_token"} # Falta password
    )
    assert response.status_code == 422


# --- Pruebas para GET /check-email/{email} ---

def test_check_email_exists_true(mocker):
    """Prueba verificar email que sí existe."""
    test_email = "exists@example.com"

    # Mockear check_email para que devuelva True
    mock_check = AsyncMock(return_value=True)
    mocker.patch.object(auth_routes_module, 'check_email', mock_check)

    response = client.get(f"{AUTH_ROUTE_PREFIX}/check-email/{test_email}")

    assert response.status_code == 200
    assert response.json() == {"exists": True}
    mock_check.assert_awaited_once_with(test_email)

def test_check_email_exists_false(mocker):
    """Prueba verificar email que no existe."""
    test_email = "doesnotexist@example.com"

    # Mockear check_email para que devuelva False
    mock_check = AsyncMock(return_value=False)
    mocker.patch.object(auth_routes_module, 'check_email', mock_check)

    response = client.get(f"{AUTH_ROUTE_PREFIX}/check-email/{test_email}")

    assert response.status_code == 200
    assert response.json() == {"exists": False}
    mock_check.assert_awaited_once_with(test_email)