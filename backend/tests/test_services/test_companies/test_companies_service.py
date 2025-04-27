
from pydantic import ValidationError
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, ANY, MagicMock
from fastapi import HTTPException
from bson import ObjectId
import stripe 
from pymongo import ReturnDocument 

from app.services.company_services import (
    fetch_companies,
    register_new_company,
    fetch_company_profile,
    update_company_profile,
    get_entity_types1,
    get_current_plan,
    request_gdpr_action,
    request_account_deletion,
    update_data_sharing_consent,
    get_data_sharing_consent,
    get_delete_account_request,
    get_gdpr_logs,
    StripeService,
    confirmar_pago,
    check_expired_subscriptions
)
from app.models.company import (
    CompanyResponse,
    CompanyCreate,
    UpdateCompanyProfile,
    EntityType,
    SubscriptionPlan
)
from app.utils.security import hash_password 

# Ruta al módulo bajo prueba
MODULE_PATH = "app.services.company_services"

# --- Clase de Pruebas ---
class TestCompanyServices:

    # --- Pruebas para fetch_companies ---

    @pytest.mark.asyncio
    async def test_fetch_companies_success(self, mocker):
        """Prueba que fetch_companies devuelve una lista de empresas."""
        # Datos simulados (asegúrate que tienen todos los campos requeridos por CompanyResponse)
        mock_now_iso = datetime(2024, 4, 27, 18, 0, 0).isoformat()
        mock_company_list = [
            {
                "_id": ObjectId(), "name": "Company A", "email": "a@test.com",
                "industry": "Tech", "country": "ES",
                "created_at": mock_now_iso, "updated_at": mock_now_iso
            },
            {
                "_id": ObjectId(), "name": "Company B", "email": "b@test.com",
                "industry": "Finance", "country": "UK",
                "created_at": mock_now_iso, "updated_at": mock_now_iso
            },
        ]
        # 1. Mock para el objeto cursor (NO es async)
        mock_cursor = MagicMock()
        # 2. El método to_list del cursor SÍ es async y devuelve la lista
        mock_cursor.to_list = AsyncMock(return_value=mock_company_list)

        # 3. Mock para el objeto colección (db.companies) (NO es async)
        mock_companies_collection = MagicMock()
        # 4. El método find de la colección devuelve síncronamente el cursor mock
        mock_companies_collection.find = MagicMock(return_value=mock_cursor)

        # 5. Parcheamos el atributo 'companies' del objeto 'db' dentro del módulo
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Llamar a la función
        result = await fetch_companies()

        # Verificaciones
        # Verificar que se llamó a find() en la colección mock
        mock_companies_collection.find.assert_called_once_with()
        # Verificar que se llamó y esperó a to_list() en el cursor mock
        mock_cursor.to_list.assert_awaited_once_with(length=None)

        # Verificar el resultado (como antes)
        assert len(result) == 2
        assert isinstance(result[0], CompanyResponse)
        assert result[0].name == "Company A"
        assert result[0].country == "ES"
        assert isinstance(result[0].created_at, datetime) # Pydantic convierte
        assert result[1].name == "Company B"


    @pytest.mark.asyncio
    async def test_fetch_companies_empty(self, mocker):
        """Prueba fetch_companies cuando no hay empresas."""
        # Mockear find().to_list() para devolver lista vacía
        mock_company_list_or_empty = []  # Lista vacía para simular sin empresas
        mock_cursor = MagicMock()  # El cursor en sí no es async
        # El método to_list del cursor SÍ es async y devuelve la lista deseada
        mock_cursor.to_list = AsyncMock(return_value=mock_company_list_or_empty) # Reemplaza con la lista real o vacía

        mock_companies_collection = MagicMock() # La colección no necesita ser async para este mock
        mock_companies_collection.find = MagicMock(return_value=mock_cursor) # find() devuelve el cursor mock síncronamente
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        result = await fetch_companies()

        mock_companies_collection.find.assert_called_once_with()
        mock_cursor.to_list.assert_awaited_once_with(length=None)
        assert len(result) == 0
        assert result == []

    # --- Pruebas para register_new_company ---

    # Datos de prueba válidos para CompanyCreate
    valid_company_data = {
        "name": "NewCo", "email": "newco@test.com", "password": "password123",
        "confirm_password": "password123", "industry": "Retail", "country": "ES",
        "phone_number": "123456789", "tax_id": "B12345678", "address": "123 Main St",
        "founded_date": datetime(2020, 1, 1), "entity_type": EntityType.SL,
        "billing_account_number": "ES9121000418401234567891",
        "terms_accepted": True, "privacy_policy_accepted": True, "data_processing_consent": True
    }

    @pytest.mark.asyncio
    async def test_register_new_company_success(self, mocker):
        """Prueba el registro exitoso de una nueva empresa."""
        company_input = CompanyCreate(**self.valid_company_data)
        hashed_pass = "hashed_password_value"
        inserted_id = ObjectId()

        # 1. Define la fecha/hora mock PRIMERO
        mock_now = datetime(2024, 4, 27, 17, 0, 0)

        # 2. Mockea dependencias (como datetime) USANDO mock_now
        mock_hash = mocker.patch(f"{MODULE_PATH}.hash_password", return_value=hashed_pass)
        mock_datetime = MagicMock()
        mock_datetime.utcnow.return_value = mock_now # mock_now ya está definido
        mocker.patch(f"{MODULE_PATH}.datetime", mock_datetime) # Parchea datetime en el módulo


        # 3. Mockea DB (como lo tenías antes está bien)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=None)
        mock_companies_collection.insert_one = AsyncMock()
        mock_companies_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Llamar a la función
        result = await register_new_company(company_input)

        # Verificaciones (sin cambios aquí)
        mock_companies_collection.find_one.assert_awaited_once_with({"email": company_input.email})
        mock_hash.assert_called_once_with(company_input.password)
        mock_companies_collection.insert_one.assert_awaited_once()
        call_args, _ = mock_companies_collection.insert_one.await_args
        inserted_doc = call_args[0]
        assert inserted_doc["email"] == company_input.email
        assert inserted_doc["password"] == hashed_pass
        assert "confirm_password" not in inserted_doc
        # Ahora usamos mock_now para verificar los timestamps
        assert inserted_doc["created_at"] == mock_now.isoformat()
        assert inserted_doc["updated_at"] == mock_now.isoformat()
        assert inserted_doc["consent_timestamp"] == mock_now.isoformat()
        assert inserted_doc["terms_accepted"] is True

        assert isinstance(result, CompanyResponse)
        assert result.id == str(inserted_id)
        assert result.name == company_input.name
        assert result.email == company_input.email
        assert result.created_at == mock_now

    @pytest.mark.asyncio
    async def test_register_new_company_terms_not_accepted(self, mocker):
        """Prueba fallo si no se aceptan los términos."""
        invalid_data = self.valid_company_data.copy()
        invalid_data["terms_accepted"] = False
        company_input = CompanyCreate(**invalid_data)

        with pytest.raises(HTTPException) as exc_info:
            await register_new_company(company_input)
        assert exc_info.value.status_code == 400
        assert "Debes aceptar los términos" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_register_new_company_password_mismatch(self, mocker):
        """Prueba fallo si las contraseñas no coinciden (espera ValidationError)."""
        # Importar ValidationError al principio del archivo
        from pydantic import ValidationError

        invalid_data = self.valid_company_data.copy()
        invalid_data["confirm_password"] = "different_password"

        with pytest.raises(ValidationError):
             CompanyCreate(**invalid_data)


    @pytest.mark.asyncio
    async def test_register_new_company_email_exists(self, mocker):
        """Prueba fallo si el email ya está registrado."""
        company_input = CompanyCreate(**self.valid_company_data)

        # Mockear find_one para que devuelva una empresa existente
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value={"email": company_input.email})
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        mock_hash = mocker.patch(f"{MODULE_PATH}.hash_password") # No debería llamarse

        with pytest.raises(HTTPException) as exc_info:
            await register_new_company(company_input)

        assert exc_info.value.status_code == 400
        assert "La empresa ya está registrada" in exc_info.value.detail
        mock_companies_collection.find_one.assert_awaited_once_with({"email": company_input.email})
        mock_hash.assert_not_called() # No se hashea si el email existe



    @pytest.mark.asyncio
    async def test_fetch_company_profile_found(self, mocker):
        """Prueba obtener el perfil de una empresa existente."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7" # ID válido como string
        test_company_id_obj = ObjectId(test_company_id_str)
        mock_now_iso = datetime.utcnow().isoformat()

        # Datos simulados devueltos por la BD
        mock_company_data = {
            "_id": test_company_id_obj,
            "name": "Test Profile Co",
            "email": "profile@test.com",
            "industry": "Testing",
            "country": "PY",
            "created_at": mock_now_iso,
            "updated_at": mock_now_iso,
            "subscription_plan": SubscriptionPlan.PRO # Añadir otros campos si son necesarios para CompanyResponse
        }

        # Mockear la colección db.companies
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Llamar a la función
        result = await fetch_company_profile(test_company_id_str)

        # Verificaciones
        mock_companies_collection.find_one.assert_awaited_once_with({"_id": test_company_id_obj})
        assert isinstance(result, CompanyResponse)
        assert result.id == test_company_id_str
        assert result.name == "Test Profile Co"
        assert result.email == "profile@test.com"
        assert result.country == "PY"
        assert result.subscription_plan == SubscriptionPlan.PRO

    @pytest.mark.asyncio
    async def test_fetch_company_profile_not_found(self, mocker):
        """Prueba obtener el perfil de una empresa que no existe."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a8" # Otro ID
        test_company_id_obj = ObjectId(test_company_id_str)

        # Mockear find_one para que devuelva None
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=None)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Verificar que lanza HTTPException 404
        with pytest.raises(HTTPException) as exc_info:
            await fetch_company_profile(test_company_id_str)

        assert exc_info.value.status_code == 404
        assert "Empresa no encontrada" in exc_info.value.detail
        mock_companies_collection.find_one.assert_awaited_once_with({"_id": test_company_id_obj})

    # --- Pruebas para update_company_profile ---

    @pytest.mark.asyncio
    async def test_update_company_profile_success(self, mocker):
        """Prueba actualizar el perfil de una empresa existente."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        mock_now = datetime(2024, 4, 27, 19, 0, 0) # Hora fija para updated_at
        mock_now_iso = mock_now.isoformat()

        # Datos de entrada para la actualización (modelo Pydantic)
        update_data_input = UpdateCompanyProfile(
            name="Updated Test Co",
            industry="Updated Industry",
            country="DE",
            email="update@test.com",          # Proporciona un email válido
            founded_date=datetime(2021, 1, 1)
            
            # Solo incluimos los campos a actualizar
        )

        # Datos de la empresa ANTES de actualizar (devueltos por el primer find_one)
        existing_company_data = {
            "_id": test_company_id_obj, "name": "Old Name", "email": "update@test.com",
            "industry": "Old Industry", "country": "FR", "created_at": datetime.utcnow().isoformat(),
             "updated_at": datetime.utcnow().isoformat() # Timestamp antiguo
        }

        # Datos de la empresa DESPUÉS de actualizar (devueltos por el segundo find_one)
        updated_company_data_from_db = {
            "_id": test_company_id_obj, "name": "Updated Test Co", "email": "update@test.com",
            "industry": "Updated Industry", "country": "DE", "created_at": existing_company_data["created_at"],
            "updated_at": mock_now_iso # Timestamp actualizado
             # Asegurarse que tiene todos los campos requeridos por CompanyResponse
        }

        # Mockear datetime.utcnow para controlar el timestamp 'updated_at'
        mock_datetime = MagicMock()
        mock_datetime.utcnow.return_value = mock_now
        mocker.patch(f"{MODULE_PATH}.datetime", mock_datetime)

        # Mockear la colección db.companies
        mock_companies_collection = AsyncMock()
        # Configurar las dos llamadas a find_one
        mock_companies_collection.find_one.side_effect = [
            existing_company_data, # Primera llamada (check exists)
            updated_company_data_from_db # Segunda llamada (re-fetch)
        ]
        mock_companies_collection.update_one = AsyncMock() # Mockear update_one
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Llamar a la función
        result = await update_company_profile(test_company_id_str, update_data_input)

        # Verificaciones
        assert mock_companies_collection.find_one.await_count == 2 # Se llamó dos veces
        # Verificar la primera llamada a find_one
        assert mock_companies_collection.find_one.await_args_list[0].args == ({"_id": test_company_id_obj},)
        # Verificar la llamada a update_one
        mock_companies_collection.update_one.assert_awaited_once()
        update_call_args, _ = mock_companies_collection.update_one.await_args
        assert update_call_args[0] == {"_id": test_company_id_obj} # Filtro
        expected_update_set = update_data_input.dict(exclude_unset=True) # Datos del input Pydantic
        expected_update_set["updated_at"] = mock_now_iso # Añadir timestamp
        assert update_call_args[1] == {"$set": expected_update_set} # Documento de actualización
        # Verificar la segunda llamada a find_one
        assert mock_companies_collection.find_one.await_args_list[1].args == ({"_id": test_company_id_obj},)

        # Verificar el resultado
        assert isinstance(result, CompanyResponse)
        assert result.id == test_company_id_str
        assert result.name == "Updated Test Co"
        assert result.industry == "Updated Industry"
        assert result.country == "DE"
        assert result.updated_at == mock_now # Pydantic convierte ISO a datetime

    @pytest.mark.asyncio
    async def test_update_company_profile_not_found(self, mocker):
        """Prueba actualizar perfil de empresa que no existe."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a8"
        test_company_id_obj = ObjectId(test_company_id_str)
        update_data_input = UpdateCompanyProfile(name="Doesnt Matter",email="notfound@test.com",        # Proporciona un email válido
    founded_date=datetime(2022, 1, 1))

        # Mockear find_one para que devuelva None en la primera llamada
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=None)
        mock_companies_collection.update_one = AsyncMock() # No debería llamarse
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        # Verificar que lanza HTTPException 404
        with pytest.raises(HTTPException) as exc_info:
            await update_company_profile(test_company_id_str, update_data_input)

        assert exc_info.value.status_code == 404
        assert "Empresa no encontrada" in exc_info.value.detail
        # Verificar que find_one se llamó (solo una vez)
        mock_companies_collection.find_one.assert_awaited_once_with({"_id": test_company_id_obj})
        # Verificar que update_one no se llamó
        mock_companies_collection.update_one.assert_not_awaited()


    @pytest.mark.asyncio
    async def test_get_entity_types1(self): # Añade async
        """Prueba que get_entity_types1 devuelve todos los miembros del Enum EntityType."""
        # --- Usa await al llamar a la función ---
        result = await get_entity_types1() # Añade await

        # Verifica que el resultado es una lista de todos los miembros del Enum
        expected_types = list(EntityType)
        assert result == expected_types
        assert len(result) == len(EntityType)
        assert EntityType.SL in result

    # --- Pruebas para get_current_plan ---

    @pytest.mark.asyncio
    async def test_get_current_plan_found(self, mocker):
        """Prueba obtener el plan actual de una empresa."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        # Simular empresa con plan PRO
        mock_company_data = {"_id": test_company_id_obj, "subscription_plan": SubscriptionPlan.PRO}

        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        result = await get_current_plan(test_company_id_str)

        mock_companies_collection.find_one.assert_awaited_once_with({"_id": test_company_id_obj})
        assert result == SubscriptionPlan.PRO

    @pytest.mark.asyncio
    async def test_get_current_plan_default_basic(self, mocker):
        """Prueba obtener el plan cuando no está definido (debería default a BASICO o 0 según el código)."""
        # Nota: El código original devuelve 0 si no existe, pero podría ser mejor devolver BASICO. Ajusta la aserción.
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        mock_company_data = {"_id": test_company_id_obj} # Sin campo subscription_plan

        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_company_data)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        result = await get_current_plan(test_company_id_str)

        mock_companies_collection.find_one.assert_awaited_once_with({"_id": test_company_id_obj})
        # Ajusta esta aserción según el comportamiento esperado de tu función:
        assert result == 0 # O assert result == SubscriptionPlan.BASICO

    @pytest.mark.asyncio
    async def test_get_current_plan_not_found(self, mocker):
        """Prueba obtener plan de empresa inexistente."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a8"
        test_company_id_obj = ObjectId(test_company_id_str)

        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=None) # No encontrado
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_plan(test_company_id_str)
        assert exc_info.value.status_code == 404

    # --- Pruebas para request_gdpr_action ---

    @pytest.mark.asyncio
    async def test_request_gdpr_action_success(self, mocker):
        """Prueba registrar una acción GDPR exitosamente."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        test_action = "access"

        # Mockear update_one para simular éxito (modified_count=1)
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 1
        mock_companies_collection = AsyncMock()
        mock_companies_collection.update_one = AsyncMock(return_value=mock_update_result)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        await request_gdpr_action(test_company_id_str, test_action)

        # Verificar llamada a update_one con $push
        mock_companies_collection.update_one.assert_awaited_once_with(
            {"_id": test_company_id_obj},
            {"$push": {"gdpr_request_log": {"action": test_action}}}
        )

    @pytest.mark.asyncio
    async def test_request_gdpr_action_failure(self, mocker):
        """Prueba fallo al registrar acción GDPR (ej: empresa no encontrada)."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        test_action = "delete"

        # Mockear update_one para simular fallo (modified_count=0)
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 0
        mock_companies_collection = AsyncMock()
        mock_companies_collection.update_one = AsyncMock(return_value=mock_update_result)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        with pytest.raises(HTTPException) as exc_info:
            await request_gdpr_action(test_company_id_str, test_action)
        assert exc_info.value.status_code == 400
        assert "No se pudo registrar la solicitud GDPR" in exc_info.value.detail

    # --- Pruebas para request_account_deletion --- (Similar a GDPR)

    @pytest.mark.asyncio
    async def test_request_account_deletion_success(self, mocker):
        """Prueba solicitar eliminación de cuenta exitosamente."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)

        mock_update_result = MagicMock(modified_count=1)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.update_one = AsyncMock(return_value=mock_update_result)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        await request_account_deletion(test_company_id_str)

        mock_companies_collection.update_one.assert_awaited_once_with(
            {"_id": test_company_id_obj},
            {"$set": {"account_deletion_requested": True}}
        )

    @pytest.mark.asyncio
    async def test_request_account_deletion_failure(self, mocker):
        """Prueba fallo al solicitar eliminación de cuenta."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)

        mock_update_result = MagicMock(modified_count=0)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.update_one = AsyncMock(return_value=mock_update_result)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        with pytest.raises(HTTPException) as exc_info:
            await request_account_deletion(test_company_id_str)
        assert exc_info.value.status_code == 400
        assert "No se pudo solicitar la eliminación de cuenta" in exc_info.value.detail

    # --- Pruebas para update_data_sharing_consent --- (Similar a Deletion)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("consent_value", [True, False]) # Probar ambos valores
    async def test_update_data_sharing_consent_success(self, mocker, consent_value):
        """Prueba actualizar consentimiento de compartir datos."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)

        mock_update_result = MagicMock(modified_count=1)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.update_one = AsyncMock(return_value=mock_update_result)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        await update_data_sharing_consent(test_company_id_str, consent_value)

        mock_companies_collection.update_one.assert_awaited_once_with(
            {"_id": test_company_id_obj},
            {"$set": {"data_sharing_consent": consent_value}}
        )

    @pytest.mark.asyncio
    async def test_update_data_sharing_consent_failure(self, mocker):
        """Prueba fallo al actualizar consentimiento."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)

        mock_update_result = MagicMock(modified_count=0)
        mock_companies_collection = AsyncMock()
        mock_companies_collection.update_one = AsyncMock(return_value=mock_update_result)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        with pytest.raises(HTTPException) as exc_info:
            await update_data_sharing_consent(test_company_id_str, True)
        assert exc_info.value.status_code == 400
        assert "No se pudo actualizar el consentimiento" in exc_info.value.detail

    # --- Pruebas para GETTERS (get_data_sharing_consent, get_delete_account_request, get_gdpr_logs) ---
    # Usan find_one con proyección

    @pytest.mark.asyncio
    async def test_get_data_sharing_consent_found(self, mocker):
        """Prueba obtener consentimiento existente."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        mock_consent_data = {"data_sharing_consent": True}

        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_consent_data)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        result = await get_data_sharing_consent(test_company_id_str)

        mock_companies_collection.find_one.assert_awaited_once_with(
            {"_id": test_company_id_obj}, {"data_sharing_consent": 1, "_id": 0} # Verificar proyección
        )
        assert result == mock_consent_data

    @pytest.mark.asyncio
    async def test_get_data_sharing_consent_not_found(self, mocker):
        """Prueba obtener consentimiento de empresa inexistente."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a8"
        test_company_id_obj = ObjectId(test_company_id_str)

        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=None) # No encontrado
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)

        with pytest.raises(HTTPException) as exc_info:
            await get_data_sharing_consent(test_company_id_str)
        assert exc_info.value.status_code == 404

    # (Añadir pruebas similares para get_delete_account_request y get_gdpr_logs,
    #  ajustando el campo en la proyección y el valor devuelto)
    @pytest.mark.asyncio
    async def test_get_delete_account_request_found(self, mocker):
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        mock_data = {"account_deletion_requested": True}
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_data)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        result = await get_delete_account_request(test_company_id_str)
        mock_companies_collection.find_one.assert_awaited_once_with(
            {"_id": test_company_id_obj}, {"account_deletion_requested": 1, "_id": 0}
        )
        assert result == mock_data

    @pytest.mark.asyncio
    async def test_get_gdpr_logs_found(self, mocker):
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        mock_logs = [{"action": "access"}, {"action": "delete"}]
        mock_data = {"gdpr_request_log": mock_logs}
        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one = AsyncMock(return_value=mock_data)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        result = await get_gdpr_logs(test_company_id_str)
        mock_companies_collection.find_one.assert_awaited_once_with(
            {"_id": test_company_id_obj}, {"gdpr_request_log": 1, "_id": 0}
        )
        assert result == mock_logs


    # --- Pruebas para StripeService.create_checkout_session ---

    def test_stripe_service_create_checkout_session_success(self, mocker):
        """Prueba la creación exitosa de una sesión de Stripe."""
        test_company_id = "comp_stripe_123"
        expected_session_url = "https://checkout.stripe.com/pay/cs_test_12345"
        mock_session = MagicMock()
        mock_session.url = expected_session_url

        # Mockear stripe.checkout.Session.create
        # === CORRECCIÓN AQUÍ: Usar return_value para el caso de éxito ===
        mock_stripe_create = mocker.patch('stripe.checkout.Session.create', return_value=mock_session)
        # === FIN CORRECCIÓN ===

        # Llamar al método estático
        result_url = StripeService.create_checkout_session(test_company_id)

        # Verificaciones (sin cambios aquí)
        assert result_url == expected_session_url
        mock_stripe_create.assert_called_once()
        call_args, call_kwargs = mock_stripe_create.call_args
        assert call_kwargs['payment_method_types'] == ["card"]
        assert call_kwargs['mode'] == "payment"
        assert call_kwargs['client_reference_id'] == test_company_id
        assert call_kwargs['success_url'] == "http://localhost:3000/confirm-plan"
        assert call_kwargs['cancel_url'] == "http://localhost:3000/subscriptions"
        assert len(call_kwargs['line_items']) == 1
        assert call_kwargs['line_items'][0]['price_data']['currency'] == "eur"
        assert call_kwargs['line_items'][0]['price_data']['unit_amount'] == 1999
        assert call_kwargs['line_items'][0]['quantity'] == 1


    def test_stripe_service_create_checkout_session_failure(self, mocker):
        """Prueba el manejo de errores de la API de Stripe."""
        test_company_id = "comp_stripe_456"

        # Mockear stripe.checkout.Session.create para que lance un error
        # === CORRECCIÓN AQUÍ: Usar APIConnectionError (API en mayúsculas) ===
        mock_stripe_create = mocker.patch('stripe.checkout.Session.create', side_effect=stripe.error.APIConnectionError("Stripe connection failed"))
        # === FIN CORRECCIÓN ===

        # Verificar que lanza HTTPException 500
        with pytest.raises(HTTPException) as exc_info:
            StripeService.create_checkout_session(test_company_id)

        assert exc_info.value.status_code == 500
        assert "Error al crear la sesión de pago" in exc_info.value.detail
        mock_stripe_create.assert_called_once()

    # --- Pruebas para confirmar_pago ---

    @pytest.mark.asyncio
    async def test_confirmar_pago_success(self, mocker):
        """Prueba la confirmación de pago y actualización de plan."""
        test_company_id_str = "60d5ec49a5a0a2f9a4a5a6a7"
        test_company_id_obj = ObjectId(test_company_id_str)
        mock_now = datetime(2024, 5, 1, 10, 0, 0) # Hora fija
        expected_expiry = mock_now + timedelta(days=30)

        mock_updated_company = {
            "_id": test_company_id_obj, "name": "Paid Co",
            "subscription_plan": SubscriptionPlan.PRO,
            "subscription_expires_at": expected_expiry
        }

        mock_datetime = MagicMock()
        mock_datetime.utcnow.return_value = mock_now
        mocker.patch(f"{MODULE_PATH}.datetime", mock_datetime)

        mock_companies_collection = AsyncMock()
        mock_companies_collection.find_one_and_update = AsyncMock(return_value=mock_updated_company)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        mock_invoices_collection = AsyncMock()
        mock_invoices_collection.insert_one = AsyncMock()
        mocker.patch(f"{MODULE_PATH}.db.invoices", mock_invoices_collection)

        result = await confirmar_pago(test_company_id_obj)

        mock_companies_collection.find_one_and_update.assert_awaited_once()
        # === CORRECCIÓN AQUÍ: Capturar kwargs y usarlo para la aserción ===
        call_args_update, call_kwargs_update = mock_companies_collection.find_one_and_update.await_args
        # === FIN CORRECCIÓN ===

        assert call_args_update[0] == {"_id": test_company_id_obj} # Filtro (args[0])
        assert call_args_update[1]["$set"]["subscription_plan"] == SubscriptionPlan.PRO # Update (args[1])
        assert isinstance(call_args_update[1]["$set"]["subscription_expires_at"], datetime)
        assert abs(call_args_update[1]["$set"]["subscription_expires_at"] - expected_expiry) < timedelta(seconds=5)

        # === CORRECCIÓN AQUÍ: Usar kwargs para verificar return_document ===
        assert call_kwargs_update['return_document'] == ReturnDocument.AFTER # Verificar opción en kwargs
        # === FIN CORRECCIÓN ===

        mock_invoices_collection.insert_one.assert_awaited_once()
        call_args_invoice, _ = mock_invoices_collection.insert_one.await_args
        invoice_doc = call_args_invoice[0]
        assert invoice_doc["company_id"] == test_company_id_str
        # ... (resto de aserciones de invoice) ...

        assert result["status"] == "success"
        assert result["message"] == "Plan actualizado correctamente"
        assert result["expires_at"] == expected_expiry

    # --- Pruebas para check_expired_subscriptions ---

    @pytest.mark.asyncio
    async def test_check_expired_subscriptions_updates_expired(self, mocker):
        """Prueba que check_expired_subscriptions degrada planes expirados."""
        mock_now = datetime(2024, 5, 1, 12, 0, 0)

        # Mockear datetime
        mock_datetime = MagicMock()
        mock_datetime.utcnow.return_value = mock_now
        mocker.patch(f"{MODULE_PATH}.datetime", mock_datetime)

        # Mockear update_many
        mock_update_result = MagicMock(modified_count=3) # Simular 3 modificados
        mock_companies_collection = AsyncMock()
        mock_companies_collection.update_many = AsyncMock(return_value=mock_update_result)
        mocker.patch(f"{MODULE_PATH}.db.companies", mock_companies_collection)
        # Mockear print para evitar salida en consola (opcional)
        mocker.patch('builtins.print')

        # Llamar a la función
        await check_expired_subscriptions()

        # Verificar llamada a update_many
        mock_companies_collection.update_many.assert_awaited_once()
        call_args, _ = mock_companies_collection.update_many.await_args
        # Verificar filtro
        assert call_args[0] == {"subscription_plan": SubscriptionPlan.PRO, "subscription_expires_at": {"$lt": mock_now}}
        # Verificar documento de actualización
        assert call_args[1] == {"$set": {"subscription_plan": SubscriptionPlan.BASICO}, "$unset": {"subscription_expires_at": ""}}