
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, ANY, MagicMock
from fastapi import HTTPException

from app.services.auth_services import (
    authenticate_user,
    send_email,
    generate_reset_token,
    reset_user_password,
    check_email,
    MAX_FAILED_ATTEMPTS,
    LOCKOUT_TIME,
    settings 
)
from app.utils.security import verify_password, create_access_token, hash_password
import app.services.company_services 
import smtplib 
import secrets 

MODULE_PATH = "app.services.auth_services"

class TestAuthServices:


    def test_send_email_success(self, mocker):
        """Prueba que send_email construye y envía el correo correctamente."""
        # Mockear la configuración (asumiendo que se usa settings directamente)
        mocker.patch(f"{MODULE_PATH}.settings.email_name", "Test Sender")
        mocker.patch(f"{MODULE_PATH}.settings.email_from", "sender@test.com")
        mocker.patch(f"{MODULE_PATH}.settings.email_host", "smtp.test.com")
        mocker.patch(f"{MODULE_PATH}.settings.email_port", 587)
        mocker.patch(f"{MODULE_PATH}.settings.email_user", "user")
        mocker.patch(f"{MODULE_PATH}.settings.email_password", "pass")

        # Mockear smtplib.SMTP y sus métodos
        mock_smtp_instance = MagicMock() # Usamos MagicMock para simular métodos mágicos como __enter__/__exit__
        mock_smtp_context_manager = MagicMock()
        mock_smtp_context_manager.__enter__.return_value = mock_smtp_instance # El 'with' devuelve la instancia

        mock_smtp_class = mocker.patch('smtplib.SMTP', return_value=mock_smtp_context_manager)

        # Datos de prueba
        to_email = "recipient@test.com"
        subject = "Test Subject"
        content = "<p>Test Content</p>"

        # Llamar a la función
        send_email(to_email, subject, content)

        # Verificaciones
        mock_smtp_class.assert_called_once_with("smtp.test.com", 587) # Verificar conexión inicial
        mock_smtp_instance.starttls.assert_called_once() # Verificar starttls
        mock_smtp_instance.login.assert_called_once_with("user", "pass") # Verificar login
        mock_smtp_instance.sendmail.assert_called_once() # Verificar que se intentó enviar

        # Verificar los argumentos de sendmail (un poco más complejo por MIMEText)
        call_args, _ = mock_smtp_instance.sendmail.call_args
        assert call_args[0] == "sender@test.com" # From
        assert call_args[1] == to_email # To
        assert f"To: {to_email}" in call_args[2] # Verificar que el 'To' está en el mensaje string
        assert f"Subject: {subject}" in call_args[2] # Verificar Subject
        assert content in call_args[2] # Verificar contenido HTML

    def test_send_email_failure(self, mocker):
        """Prueba que send_email maneja excepciones de smtplib."""
        # Mockear settings (igual que antes)
        mocker.patch(f"{MODULE_PATH}.settings.email_from", "sender@test.com")
        # ... (mockear el resto de settings relevantes si es necesario) ...
        mocker.patch(f"{MODULE_PATH}.settings.email_host", "smtp.test.com")
        mocker.patch(f"{MODULE_PATH}.settings.email_port", 587)

        # Mockear smtplib.SMTP para que lance un error al conectar
        mocker.patch('smtplib.SMTP', side_effect=Exception("Simulated Connection failed"))

        try:
             send_email("recipient@test.com", "Subject", "Content")
        except Exception as e:
             pytest.fail(f"send_email lanzó una excepción inesperada: {e}")

    # --- Pruebas para check_email (Asíncrona) ---

    @pytest.mark.asyncio
    async def test_check_email_found(self, mocker):
        """Prueba que check_email devuelve True si el email existe."""
        test_email = "exists@test.com"

        mock_companies_collection = AsyncMock() # Mock para la colección entera
        mock_companies_collection.find_one = AsyncMock(return_value={"email": test_email, "_id": "some_id"}) # Añadimos el método mockeado
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection) # Parcheamos la colección

        result = await check_email(test_email)

        mock_companies_collection.find_one.assert_called_once_with({"email": test_email}) # Verificamos sobre el método del nuevo mock
        assert result is True

    @pytest.mark.asyncio
    async def test_check_email_not_found(self, mocker):
        """Prueba que check_email devuelve False si el email no existe."""
        test_email = "notfound@test.com"

        mock_companies_collection = AsyncMock() # Mock para la colección entera
        mock_companies_collection.find_one = AsyncMock(return_value=None) # Añadimos el método mockeado
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection) # Parcheamos la colección

        result = await check_email(test_email)

        mock_companies_collection.find_one.assert_called_once_with({"email": test_email}) # Verificamos sobre el método del nuevo mock
        assert result is False


    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mocker):
        """Prueba autenticación exitosa para usuario válido y no bloqueado."""
        test_email = "valid@test.com"
        test_password = "correct_password"
        hashed_password = "hashed_correct_password" # Simulado
        company_id = "comp_123"
        expected_token = "fake_jwt_token"

        # Mock de la compañía devuelta por la BD
        mock_company_data = {
            "_id": company_id,
            "email": test_email,
            "password": hashed_password,
            "account_locked": False,
            "failed_login_attempts": 0
        }

        # Mockear dependencias
        mock_check_expired = mocker.patch(f"{MODULE_PATH}.check_expired_subscriptions", new_callable=AsyncMock)
        mock_verify = mocker.patch(f"{MODULE_PATH}.verify_password", return_value=True)
        mock_create_token = mocker.patch(f"{MODULE_PATH}.create_access_token", return_value=expected_token)

        # Mockear DB (usando la estrategia de mockear la colección)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mock_companies_collection.update_one = AsyncMock() # Mockeamos update_one
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Llamar a la función
        token = await authenticate_user(test_email, test_password)

        # Verificaciones
        mock_check_expired.assert_awaited_once() # Verificar llamada a check_expired
        mock_companies_collection.find_one.assert_awaited_once_with({"email": test_email})
        mock_verify.assert_called_once_with(test_password, hashed_password)
        # Verificar la actualización de éxito (resetear intentos, poner last_login)
        mock_companies_collection.update_one.assert_awaited_once_with(
            {"email": test_email},
            {"$set": {
                "failed_login_attempts": 0,
                "account_locked": False,
                "last_login": ANY # Verificar que se intenta poner un datetime
            }}
        )
        mock_create_token.assert_called_once_with(data={"sub": test_email, "company_id": company_id})
        assert token == expected_token

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password_no_lock(self, mocker):
        """Prueba fallo con contraseña inválida, sin llegar a bloquear."""
        test_email = "valid@test.com"
        test_password = "wrong_password"
        hashed_password = "hashed_correct_password"
        company_id = "comp_123"

        mock_company_data = {
            "_id": company_id, "email": test_email, "password": hashed_password,
            "account_locked": False, "failed_login_attempts": 1 # Ya tenía 1 intento
        }

        mock_check_expired = mocker.patch(f"{MODULE_PATH}.check_expired_subscriptions", new_callable=AsyncMock)
        mock_verify = mocker.patch(f"{MODULE_PATH}.verify_password", return_value=False) # Contraseña falla
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mock_companies_collection.update_one = AsyncMock()
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Verificar que lanza HTTPException 401
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user(test_email, test_password)

        assert exc_info.value.status_code == 401
        assert "Credenciales inválidas" in exc_info.value.detail

        mock_check_expired.assert_awaited_once()
        mock_companies_collection.find_one.assert_awaited_once_with({"email": test_email})
        mock_verify.assert_called_once_with(test_password, hashed_password)
        # Verificar la actualización de fallo (incrementar intentos)
        mock_companies_collection.update_one.assert_awaited_once_with(
            {"email": test_email},
            {"$set": {"failed_login_attempts": 2}} # Incrementa de 1 a 2
        )

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password_triggers_lock(self, mocker):
        """Prueba fallo con contraseña inválida que causa bloqueo."""
        test_email = "valid@test.com"
        test_password = "wrong_password"
        hashed_password = "hashed_correct_password"
        company_id = "comp_123"

        # Usuario está a 1 intento del bloqueo
        mock_company_data = {
            "_id": company_id, "email": test_email, "password": hashed_password,
            "account_locked": False, "failed_login_attempts": MAX_FAILED_ATTEMPTS - 1
        }

        mock_check_expired = mocker.patch(f"{MODULE_PATH}.check_expired_subscriptions", new_callable=AsyncMock)
        mock_verify = mocker.patch(f"{MODULE_PATH}.verify_password", return_value=False) # Falla contraseña
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mock_companies_collection.update_one = AsyncMock()
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user(test_email, test_password)

        assert exc_info.value.status_code == 401

        mock_check_expired.assert_awaited_once()
        mock_companies_collection.find_one.assert_awaited_once_with({"email": test_email})
        mock_verify.assert_called_once_with(test_password, hashed_password)
        # Verificar la actualización de bloqueo
        mock_companies_collection.update_one.assert_awaited_once_with(
            {"email": test_email},
            {"$set": {
                "failed_login_attempts": MAX_FAILED_ATTEMPTS,
                "account_locked": True,
                "lockout_until": ANY # Verificar que se intenta poner fecha de bloqueo
            }}
        )
        # Comprobar que el lockout_until es un datetime futuro cercano al esperado
        call_args, call_kwargs = mock_companies_collection.update_one.call_args
        update_doc = call_kwargs.get('update', call_args[1]) # Obtener el documento de actualización
        lockout_time = update_doc["$set"]["lockout_until"]
        assert isinstance(lockout_time, datetime)
        assert lockout_time > datetime.utcnow() - timedelta(seconds=5) # Debe ser futuro
        assert abs(lockout_time - (datetime.utcnow() + LOCKOUT_TIME)) < timedelta(seconds=10) # Cercano al tiempo esperado

    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked(self, mocker):
        """Prueba intento de login con cuenta bloqueada."""
        test_email = "locked@test.com"
        test_password = "any_password"
        company_id = "comp_456"

        # Usuario bloqueado, tiempo de bloqueo aún no ha pasado
        lockout_future = datetime.utcnow() + timedelta(minutes=5)
        mock_company_data = {
            "_id": company_id, "email": test_email, "password": "some_hash",
            "account_locked": True, "lockout_until": lockout_future
        }

        mock_check_expired = mocker.patch(f"{MODULE_PATH}.check_expired_subscriptions", new_callable=AsyncMock)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mock_companies_collection.update_one = AsyncMock() # No debería llamarse
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        mock_verify = mocker.patch(f"{MODULE_PATH}.verify_password") # No debería llamarse

        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user(test_email, test_password)

        assert exc_info.value.status_code == 403
        assert "Cuenta bloqueada" in exc_info.value.detail

        mock_check_expired.assert_awaited_once()
        mock_companies_collection.find_one.assert_awaited_once_with({"email": test_email})
        mock_verify.assert_not_called() # No se verifica contraseña si está bloqueado
        mock_companies_collection.update_one.assert_not_called() # No se actualiza nada

    @pytest.mark.asyncio
    async def test_authenticate_user_account_lock_expired_auto_unlock(self, mocker):
        """Prueba login exitoso después de que el bloqueo haya expirado."""
        test_email = "unlocked@test.com"
        test_password = "correct_password"
        hashed_password = "hashed_correct_password"
        company_id = "comp_789"
        expected_token = "new_fake_token"

        # Usuario bloqueado, pero tiempo ya pasó
        lockout_past = datetime.utcnow() - timedelta(minutes=5)
        mock_company_data = {
            "_id": company_id, "email": test_email, "password": hashed_password,
            "account_locked": True, "lockout_until": lockout_past,
            "failed_login_attempts": MAX_FAILED_ATTEMPTS # Tenía intentos acumulados
        }

        mock_check_expired = mocker.patch(f"{MODULE_PATH}.check_expired_subscriptions", new_callable=AsyncMock)
        mock_verify = mocker.patch(f"{MODULE_PATH}.verify_password", return_value=True) # Contraseña correcta esta vez
        mock_create_token = mocker.patch(f"{MODULE_PATH}.create_access_token", return_value=expected_token)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mock_companies_collection.update_one = AsyncMock() # Se llamará dos veces
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        token = await authenticate_user(test_email, test_password)

        assert token == expected_token
        mock_check_expired.assert_awaited_once()
        mock_companies_collection.find_one.assert_awaited_once_with({"email": test_email})
        mock_verify.assert_called_once_with(test_password, hashed_password)

        # Verificar las DOS llamadas a update_one
        assert mock_companies_collection.update_one.await_count == 2

        # 1. Llamada de desbloqueo automático
        unlock_call = mock_companies_collection.update_one.await_args_list[0]
        assert unlock_call.args[0] == {"email": test_email}
        assert unlock_call.args[1] == {"$set": {"account_locked": False, "failed_login_attempts": 0}}

        # 2. Llamada de login exitoso
        login_success_call = mock_companies_collection.update_one.await_args_list[1]
        assert login_success_call.args[0] == {"email": test_email}
        assert login_success_call.args[1]["$set"]["failed_login_attempts"] == 0
        assert login_success_call.args[1]["$set"]["account_locked"] is False
        assert isinstance(login_success_call.args[1]["$set"]["last_login"], datetime)

        mock_create_token.assert_called_once_with(data={"sub": test_email, "company_id": company_id})

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, mocker):
        """Prueba intento de login para usuario que no existe."""
        test_email = "nonexistent@test.com"
        test_password = "any_password"

        mock_check_expired = mocker.patch(f"{MODULE_PATH}.check_expired_subscriptions", new_callable=AsyncMock)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=None) # Usuario no encontrado
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        mock_verify = mocker.patch(f"{MODULE_PATH}.verify_password") # No debería llamarse

        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user(test_email, test_password)

        assert exc_info.value.status_code == 401
        assert "Credenciales inválidas" in exc_info.value.detail

        mock_check_expired.assert_awaited_once()
        mock_companies_collection.find_one.assert_awaited_once_with({"email": test_email})
        mock_verify.assert_not_called()

    # --- Pruebas para generate_reset_token ---

    @pytest.mark.asyncio
    async def test_generate_reset_token_success(self, mocker):
        """Prueba la generación y envío de token de reseteo exitoso."""
        test_email = "user_exists@test.com"
        company_id = "comp_abc"
        fake_token = "secure_random_token_string"
        frontend_url = "http://localhost:3000" # Asumido desde settings

        mock_company_data = {"_id": company_id, "email": test_email}

        # Mockear dependencias
        mock_secrets = mocker.patch('secrets.token_urlsafe', return_value=fake_token)
        mock_send_email = mocker.patch(f"{MODULE_PATH}.send_email") # Mockear la función local
        mocker.patch(f"{MODULE_PATH}.settings.frontend_url", frontend_url) # Mockear URL frontend

        # Mockear DB
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mock_companies_collection.update_one = AsyncMock()
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Llamar a la función
        response = await generate_reset_token(test_email)

        assert response == {"message": "Correo de recuperación enviado correctamente."}

        # Verificaciones
        mock_companies_collection.find_one.assert_awaited_once_with({"email": test_email})
        mock_secrets.assert_called_once_with(32) # Verificar longitud del token
        # Verificar la actualización en BD para guardar el token
        mock_companies_collection.update_one.assert_awaited_once()
        call_args, call_kwargs = mock_companies_collection.update_one.await_args
        update_doc = call_kwargs.get('update', call_args[1])
        assert update_doc["$set"]["reset_token"] == fake_token
        assert isinstance(update_doc["$set"]["reset_token_expiration"], datetime)
        assert abs(update_doc["$set"]["reset_token_expiration"] - (datetime.utcnow() + timedelta(hours=1))) < timedelta(seconds=10)

        # Verificar llamada a send_email
        mock_send_email.assert_called_once()
        email_args = mock_send_email.call_args.args
        assert email_args[0] == test_email # to_email
        assert email_args[1] == "Recupera tu contraseña" # subject
        expected_link = f"{frontend_url}/reset-password?token={fake_token}"
        assert expected_link in email_args[2] # content (HTML)

    @pytest.mark.asyncio
    async def test_generate_reset_token_user_not_found(self, mocker):
        """Prueba generación de token cuando el usuario no existe."""
        test_email = "notfound@test.com"

        # Mockear DB para que no encuentre usuario
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=None)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        mock_send_email = mocker.patch(f"{MODULE_PATH}.send_email") # No debería llamarse

        with pytest.raises(HTTPException) as exc_info:
            await generate_reset_token(test_email)

        assert exc_info.value.status_code == 404
        assert "Este correo no existe" in exc_info.value.detail

        mock_companies_collection.find_one.assert_awaited_once_with({"email": test_email})
        mock_send_email.assert_not_called()

    # --- Pruebas para reset_user_password ---

    @pytest.mark.asyncio
    async def test_reset_user_password_success(self, mocker):
        """Prueba reseteo de contraseña exitoso con token válido."""
        valid_token = "valid_reset_token"
        new_password = "newSecurePassword123"
        hashed_new_password = "hashed_new_password" # Simulado
        company_id = "comp_def"
        user_email = "reset@test.com"

        # Usuario con token válido y no expirado
        token_expiration = datetime.utcnow() + timedelta(minutes=30)
        mock_company_data = {
            "_id": company_id, "email": user_email, "password": "old_hash",
            "reset_token": valid_token, "reset_token_expiration": token_expiration
        }

        # Mockear dependencias
        mock_hash = mocker.patch(f"{MODULE_PATH}.hash_password", return_value=hashed_new_password)

        # Mockear DB
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mock_companies_collection.update_one = AsyncMock()
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Llamar a la función
        response = await reset_user_password(valid_token, new_password)

        assert response == {"message": "Contraseña restablecida correctamente"}

        # Verificaciones
        mock_companies_collection.find_one.assert_awaited_once_with({"reset_token": valid_token})
        mock_hash.assert_called_once_with(new_password)
        # Verificar actualización (cambio de pass, quitar token)
        mock_companies_collection.update_one.assert_awaited_once_with(
            {"reset_token": valid_token},
            {
                "$set": {"password": hashed_new_password},
                "$unset": {"reset_token": "", "reset_token_expiration": ""}
            }
        )

    @pytest.mark.asyncio
    async def test_reset_user_password_token_not_found(self, mocker):
        """Prueba reseteo con token inválido."""
        invalid_token = "invalid_or_used_token"
        new_password = "newSecurePassword123"

        # Mockear DB para que no encuentre el token
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=None)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        mock_hash = mocker.patch(f"{MODULE_PATH}.hash_password") # No debería llamarse

        with pytest.raises(HTTPException) as exc_info:
            await reset_user_password(invalid_token, new_password)

        assert exc_info.value.status_code == 400
        assert "Token inválido o expirado" in exc_info.value.detail

        mock_companies_collection.find_one.assert_awaited_once_with({"reset_token": invalid_token})
        mock_hash.assert_not_called()

    @pytest.mark.asyncio
    async def test_reset_user_password_token_expired(self, mocker):
        """Prueba reseteo con token que ha expirado."""
        expired_token = "expired_reset_token"
        new_password = "newSecurePassword123"
        company_id = "comp_ghi"
        user_email = "expired@test.com"

        # Usuario con token expirado
        token_expiration_past = datetime.utcnow() - timedelta(minutes=5)
        mock_company_data = {
            "_id": company_id, "email": user_email, "password": "old_hash",
            "reset_token": expired_token, "reset_token_expiration": token_expiration_past
        }

        # Mockear DB
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        mock_hash = mocker.patch(f"{MODULE_PATH}.hash_password") # No debería llamarse
        mock_update = mocker.patch.object(mock_companies_collection, 'update_one') # No debería llamarse

        with pytest.raises(HTTPException) as exc_info:
            await reset_user_password(expired_token, new_password)

        assert exc_info.value.status_code == 400
        assert "El token ha expirado" in exc_info.value.detail

        mock_companies_collection.find_one.assert_awaited_once_with({"reset_token": expired_token})
        mock_hash.assert_not_called()
        mock_update.assert_not_called()