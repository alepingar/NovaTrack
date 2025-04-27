
import pytest
import pandas as pd
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, ANY, MagicMock
from fastapi import HTTPException
from bson import ObjectId
from uuid import UUID, uuid4 

from app.services.transfer_services import (
    fetch_transfers,
    fetch_number_transfers_per_period,
    fetch_number_anomaly_transfers_per_period,
    fetch_total_amount_per_month,
    fetch_transfer_details,
    fetch_public_summary_data,
    get_transfer_stats_by_company,
    fetch_dashboard_data_internal,
    fetch_transfers_by_filters,
    fetch_transfers1
)

MODULE_PATH = "app.services.transfer_services"

# --- Clase de Pruebas ---
class TestTransferServices:

    @pytest.mark.asyncio
    async def test_fetch_transfers_success(self, mocker): # Ya no parametrizada
        """Prueba obtener transferencias con fetch_transfers."""
        test_company_id = "comp_123"
        mock_transfer_list = [{"_id": ObjectId(), "id": str(uuid4()), "company_id": test_company_id, "amount": 100}]

        # Mock simple: find() devuelve cursor directamente
        mock_cursor = MagicMock()
        # fetch_transfers llama a to_list() sin argumentos
        mock_cursor.to_list = AsyncMock(return_value=mock_transfer_list)
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.find = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result = await fetch_transfers(test_company_id) # Llamada específica

        mock_transfers_collection.find.assert_called_once_with({"company_id": test_company_id})
        # Verificar que se llamó a to_list() SIN argumentos
        mock_cursor.to_list.assert_awaited_once_with()
        assert result == mock_transfer_list

    @pytest.mark.asyncio
    async def test_fetch_transfers_empty(self, mocker): # Ya no parametrizada
        """Prueba obtener transferencias vacías con fetch_transfers."""
        test_company_id = "comp_456"

        # Mock simple: find() devuelve cursor directamente
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[]) # Lista vacía
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.find = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result = await fetch_transfers(test_company_id) # Llamada específica

        mock_transfers_collection.find.assert_called_once_with({"company_id": test_company_id})
        # Verificar que se llamó a to_list() SIN argumentos
        mock_cursor.to_list.assert_awaited_once_with()
        assert result == []

    # --- Pruebas para fetch_transfer_details ---

    @pytest.mark.asyncio
    async def test_fetch_transfer_details_found(self, mocker):
        """Prueba obtener detalles de una transferencia existente."""
        test_company_id = "comp_abc"
        test_transfer_uuid = uuid4()
        test_transfer_id_str = str(test_transfer_uuid)
        mock_timestamp_str = datetime.utcnow().isoformat()

        mock_transfer_doc = {
            "_id": ObjectId(), "id": test_transfer_id_str, "company_id": test_company_id,
            "amount": 123.45, "timestamp": mock_timestamp_str,
            "currency": "EUR", "from_account": "ES9121000418401234567891",
            "to_account": "ES8021000813610123456789", "status": "completada",
        }

        mock_transfers_collection = AsyncMock()
        mock_transfers_collection.find_one = AsyncMock(return_value=mock_transfer_doc)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result = await fetch_transfer_details(test_company_id, test_transfer_uuid)

        mock_transfers_collection.find_one.assert_awaited_once_with({
            "id": test_transfer_id_str, "company_id": test_company_id
        })
        assert str(result.id) == test_transfer_id_str
        assert result.amount == 123.45
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_fetch_transfer_details_timestamp_is_datetime(self, mocker):
        """Prueba obtener detalles cuando timestamp ya es datetime."""
        test_company_id = "comp_abc"
        test_transfer_uuid = uuid4()
        test_transfer_id_str = str(test_transfer_uuid)
        mock_timestamp_dt = datetime.utcnow().replace(tzinfo=timezone.utc)

        mock_transfer_doc = {
             "_id": ObjectId(), "id": test_transfer_id_str,"company_id": test_company_id,
             "amount": 50.00, "timestamp": mock_timestamp_dt,
             "currency": "USD", "from_account": "GB29NWBK60161331926819",
             "to_account": "DE89370400440532013000", "status": "pendiente",
         }

        mock_transfers_collection = AsyncMock()
        mock_transfers_collection.find_one = AsyncMock(return_value=mock_transfer_doc)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result = await fetch_transfer_details(test_company_id, test_transfer_uuid)

        mock_transfers_collection.find_one.assert_awaited_once_with({
            "id": test_transfer_id_str, "company_id": test_company_id
        })
        assert str(result.id) == test_transfer_id_str
        assert result.timestamp == mock_timestamp_dt

    @pytest.mark.asyncio
    async def test_fetch_transfer_details_not_found(self, mocker):
        """Prueba obtener detalles de una transferencia inexistente."""
        test_company_id = "comp_xyz"
        test_transfer_uuid = uuid4()
        test_transfer_id_str = str(test_transfer_uuid)

        # Mockear find_one para que devuelva None
        mock_transfers_collection = AsyncMock()
        mock_transfers_collection.find_one = AsyncMock(return_value=None)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        # Verificar que lanza HTTPException 404
        with pytest.raises(HTTPException) as exc_info:
            await fetch_transfer_details(test_company_id, test_transfer_uuid)

        assert exc_info.value.status_code == 404
        assert f"No se encontró la transferencia con el ID {test_transfer_id_str}" in exc_info.value.detail
        mock_transfers_collection.find_one.assert_awaited_once_with({
            "id": test_transfer_id_str, "company_id": test_company_id
        })

    period_test_data = [
        # Caso normal 3 meses
        (2024, 5, "3months", datetime(2024, 3, 1, 0, 0, 0, tzinfo=timezone.utc), datetime(2024, 5, 31, 23, 59, 59, tzinfo=timezone.utc)),
        # Caso 3 meses cruzando año
        (2024, 2, "3months", datetime(2023, 12, 1, 0, 0, 0, tzinfo=timezone.utc), datetime(2024, 2, 29, 23, 59, 59, tzinfo=timezone.utc)), # Asumiendo 2024 bisiesto
         # Caso 1 mes
        (2024, 4, "month", datetime(2024, 4, 1, 0, 0, 0, tzinfo=timezone.utc), datetime(2024, 4, 30, 23, 59, 59, tzinfo=timezone.utc)),
        # Caso año completo
        (2023, 6, "year", datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc), datetime(2023, 6, 30, 23, 59, 59, tzinfo=timezone.utc)),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("year, month, period, expected_start, expected_end", period_test_data)
    async def test_fetch_number_transfers_per_period(self, mocker, year, month, period, expected_start, expected_end):
        """Prueba calcular número de transferencias por periodo."""
        mock_count = 55 # Número simulado de transferencias
        mock_agg_result = [{"count": mock_count}]

        # Mockear aggregate().to_list()
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_agg_result)
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        # Llamar a la función
        result_count = await fetch_number_transfers_per_period(year, month, period)

        # Verificaciones
        assert result_count == mock_count
        mock_transfers_collection.aggregate.assert_called_once() # Verificar llamada a aggregate
        # Verificar el pipeline (especialmente el $match de fechas)
        call_args, _ = mock_transfers_collection.aggregate.call_args
        pipeline = call_args[0]
        assert len(pipeline) == 2
        assert "$match" in pipeline[0]
        assert "timestamp" in pipeline[0]["$match"]
        # Comprobar fechas con un pequeño margen por si hay microsegundos
        assert abs(pipeline[0]["$match"]["timestamp"]["$gte"] - expected_start) < timedelta(seconds=1)
        assert abs(pipeline[0]["$match"]["timestamp"]["$lte"] - expected_end) < timedelta(seconds=1)
        assert pipeline[1] == {"$count": "count"}
        mock_cursor.to_list.assert_awaited_once_with(length=None)

    @pytest.mark.asyncio
    async def test_fetch_number_transfers_per_period_no_result(self, mocker):
        """Prueba calcular número de transferencias cuando la agregación no devuelve nada."""
        # Mockear aggregate().to_list() para devolver lista vacía
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[]) # Lista vacía
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result_count = await fetch_number_transfers_per_period(2024, 1, "month")

        assert result_count == 0 # Debe devolver 0 si no hay resultados
        mock_transfers_collection.aggregate.assert_called_once()
        mock_cursor.to_list.assert_awaited_once_with(length=None)


    # --- Pruebas para fetch_number_anomaly_transfers_per_period ---

    @pytest.mark.asyncio
    @pytest.mark.parametrize("year, month, period, expected_start, expected_end", period_test_data)
    async def test_fetch_number_anomaly_transfers_per_period(self, mocker, year, month, period, expected_start, expected_end):
        """Prueba calcular número de transferencias ANÓMALAS por periodo."""
        mock_count = 5 # Número simulado de anomalías
        mock_agg_result = [{"count": mock_count}]

        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_agg_result)
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result_count = await fetch_number_anomaly_transfers_per_period(year, month, period)

        assert result_count == mock_count
        mock_transfers_collection.aggregate.assert_called_once()
        call_args, _ = mock_transfers_collection.aggregate.call_args
        pipeline = call_args[0]
        assert len(pipeline) == 2
        assert "$match" in pipeline[0]
        assert "timestamp" in pipeline[0]["$match"]
        # --- Verificación CLAVE: is_anomalous ---
        assert pipeline[0]["$match"]["is_anomalous"] is True
        # --- Fin Verificación CLAVE ---
        assert abs(pipeline[0]["$match"]["timestamp"]["$gte"] - expected_start) < timedelta(seconds=1)
        assert abs(pipeline[0]["$match"]["timestamp"]["$lte"] - expected_end) < timedelta(seconds=1)
        assert pipeline[1] == {"$count": "count"}
        mock_cursor.to_list.assert_awaited_once_with(length=None)

    @pytest.mark.asyncio
    async def test_fetch_number_anomaly_transfers_per_period_no_result(self, mocker):
        """Prueba calcular número de anomalías cuando no hay resultados."""
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[]) # Lista vacía
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result_count = await fetch_number_anomaly_transfers_per_period(2024, 3, "year")

        assert result_count == 0
        mock_transfers_collection.aggregate.assert_called_once()
        mock_cursor.to_list.assert_awaited_once_with(length=None)


    # --- Pruebas para fetch_total_amount_per_month ---

    @pytest.mark.asyncio
    @pytest.mark.parametrize("year, month, period, expected_start, expected_end", period_test_data)
    async def test_fetch_total_amount_per_month(self, mocker, year, month, period, expected_start, expected_end):
        """Prueba calcular el monto total por periodo."""
        # Nota: la función se llama _per_month pero usa lógica de periodo como las otras
        mock_total = 12345.6789
        mock_agg_result = [{"total": mock_total}]

        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_agg_result)
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result_amount = await fetch_total_amount_per_month(year, month, period)

        # Verificar redondeo a 2 decimales
        assert result_amount == round(mock_total, 2)
        mock_transfers_collection.aggregate.assert_called_once()
        call_args, _ = mock_transfers_collection.aggregate.call_args
        pipeline = call_args[0]
        assert len(pipeline) == 2
        assert "$match" in pipeline[0]
        assert "timestamp" in pipeline[0]["$match"]
        # La función usa $lt para end_date aquí, no $lte como las otras
        assert abs(pipeline[0]["$match"]["timestamp"]["$gte"] - expected_start) < timedelta(seconds=1)
        assert abs(pipeline[0]["$match"]["timestamp"]["$lt"] - expected_end) < timedelta(seconds=1) # Verificar $lt
        # Verificar $group
        assert "$group" in pipeline[1]
        assert pipeline[1]["$group"] == {"_id": None, "total": {"$sum": "$amount"}}
        mock_cursor.to_list.assert_awaited_once_with(length=1) # length=1 en esta función

    @pytest.mark.asyncio
    async def test_fetch_total_amount_per_month_no_result(self, mocker):
        """Prueba calcular monto total cuando no hay resultados."""
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[]) # Lista vacía
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result_amount = await fetch_total_amount_per_month(2024, 2, "month")

        assert result_amount == 0.0 # Debe devolver 0.0
        mock_transfers_collection.aggregate.assert_called_once()
        mock_cursor.to_list.assert_awaited_once_with(length=1)
    

    @pytest.mark.asyncio
    async def test_fetch_public_summary_data_success(self, mocker):
        """Prueba obtener el resumen público de datos."""
        mock_total_transfers = 1500
        mock_total_anomalies = 75
        mock_total_amount = 123456.78

        # Mockear la colección y sus métodos
        mock_transfers_collection = AsyncMock() # Necesita ser AsyncMock por count_documents
        # Configurar side_effect para count_documents (devuelve valores distintos en orden)
        mock_transfers_collection.count_documents.side_effect = [
            mock_total_transfers,  # Primera llamada (query={})
            mock_total_anomalies   # Segunda llamada (query={"is_anomalous": True})
        ]
        # Mockear aggregate().to_list() para la suma total
        mock_agg_cursor = MagicMock()
        mock_agg_cursor.to_list = AsyncMock(return_value=[{"total": mock_total_amount}])
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_agg_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        # Llamar a la función
        result = await fetch_public_summary_data()

        # Verificaciones
        assert mock_transfers_collection.count_documents.await_count == 2
        # Verificar las llamadas a count_documents
        assert mock_transfers_collection.count_documents.await_args_list[0].args == ({},)
        assert mock_transfers_collection.count_documents.await_args_list[1].args == ({"is_anomalous": True},)
        # Verificar llamada a aggregate
        mock_transfers_collection.aggregate.assert_called_once()
        agg_call_args, _ = mock_transfers_collection.aggregate.call_args
        assert agg_call_args[0] == [{"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
        mock_agg_cursor.to_list.assert_awaited_once_with(length=1)

        # Verificar el diccionario resultado
        assert result == {
            "totalTransactions": mock_total_transfers,
            "totalAnomalies": mock_total_anomalies,
            "totalAmount": round(mock_total_amount, 2),
        }

    @pytest.mark.asyncio
    async def test_fetch_public_summary_data_no_amount(self, mocker):
        """Prueba el resumen público cuando no hay transferencias para sumar monto."""
        mock_total_transfers = 0
        mock_total_anomalies = 0

        mock_transfers_collection = AsyncMock()
        mock_transfers_collection.count_documents.side_effect = [
            mock_total_transfers, mock_total_anomalies
        ]
        # Mockear aggregate().to_list() para devolver lista vacía
        mock_agg_cursor = MagicMock()
        mock_agg_cursor.to_list = AsyncMock(return_value=[]) # Lista vacía
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_agg_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result = await fetch_public_summary_data()

        # Verificar el resultado (totalAmount debe ser 0.0)
        assert result == {
            "totalTransactions": mock_total_transfers,
            "totalAnomalies": mock_total_anomalies,
            "totalAmount": 0.0, # Asegurar que devuelve 0.0
        }
        mock_transfers_collection.aggregate.assert_called_once()
        mock_agg_cursor.to_list.assert_awaited_once_with(length=1)

    # --- Pruebas para get_transfer_stats_by_company ---

    @pytest.mark.asyncio
    async def test_get_transfer_stats_by_company_with_data(self, mocker):
        """Prueba calcular estadísticas de transferencias para una compañía con datos."""
        test_company_id = "comp_stats_1"
        # Datos simulados de la BD (solo amount y from_account)
        mock_db_data = [
            {"amount": 100.0, "from_account": "ACC_A"},
            {"amount": 150.5, "from_account": "ACC_B"},
            {"amount": 100.0, "from_account": "ACC_A"}, # Cuenta repetida
            {"amount": 200.0, "from_account": "ACC_C"},
            {"amount": 50.0,  "from_account": "ACC_B"}, # Cuenta repetida
            {"amount": 300.0, "from_account": "ACC_D"},
            {"amount": 90.0,  "from_account": "ACC_E"},
        ]

        # Mockear find().to_list()
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_db_data)
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.find = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        # Llamar a la función
        result_stats = await get_transfer_stats_by_company(test_company_id)

        # Verificaciones
        mock_transfers_collection.find.assert_called_once_with(
            {"company_id": test_company_id}, {"amount": 1, "from_account": 1} # Verificar proyección
        )
        mock_cursor.to_list.assert_awaited_once_with(length=None)

        # Verificar estadísticas (calculadas con pandas real sobre mock_db_data)
        # Puedes precalcularlas o calcularlas aquí si prefieres no mockear pandas
        expected_df = pd.DataFrame(mock_db_data)
        expected_mean = expected_df["amount"].mean()
        expected_std = expected_df["amount"].std()
        expected_q1 = expected_df["amount"].quantile(0.05)
        expected_q3 = expected_df["amount"].quantile(0.95)
        expected_recurrent = ['ACC_A', 'ACC_B'] # Cuentas con count > 1

        assert result_stats["mean"] == expected_mean
        # Comparar std con tolerancia por precisión flotante
        assert abs(result_stats["std"] - expected_std) < 0.001 if expected_std is not None and result_stats["std"] is not None else result_stats["std"] == expected_std
        assert result_stats["q1"] == expected_q1
        assert result_stats["q3"] == expected_q3
        # Comparar listas de cuentas recurrentes (el orden puede variar)
        assert sorted(result_stats["recurrent_accounts"]) == sorted(expected_recurrent)


    @pytest.mark.asyncio
    async def test_get_transfer_stats_by_company_no_data(self, mocker):
        """Prueba calcular estadísticas cuando no hay datos para la compañía."""
        test_company_id = "comp_stats_2"

        # Mockear find().to_list() para devolver lista vacía
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[]) # Lista vacía
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.find = MagicMock(return_value=mock_cursor)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)
        # Mockear DataFrame para evitar error si se intenta crear con lista vacía
        # (Aunque el código tiene un check 'if not data', es más seguro mockear)
        mocker.patch('pandas.DataFrame') # Evita que se llame a pandas real

        result_stats = await get_transfer_stats_by_company(test_company_id)

        # Verificar resultado default
        assert result_stats == {"mean": 0, "std": 0, "q1": 0, "q3": 0, "recurrent_accounts": []}
        mock_transfers_collection.find.assert_called_once_with(
             {"company_id": test_company_id}, {"amount": 1, "from_account": 1}
        )
        mock_cursor.to_list.assert_awaited_once_with(length=None)
        pd.DataFrame.assert_not_called()


    @pytest.mark.asyncio
    async def test_fetch_transfers_by_filters_no_filters(self, mocker):
        """Prueba fetch_transfers_by_filters sin filtros adicionales."""
        test_company_id = "comp_filter_1"
        mock_result_list = [{"_id": ObjectId(), "amount": 100}]

        # Mockear find().sort().to_list()
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_result_list)
        mock_find_result = MagicMock()
        mock_find_result.sort = MagicMock(return_value=mock_cursor)
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.find = MagicMock(return_value=mock_find_result)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        result = await fetch_transfers_by_filters(company_id=test_company_id)

        # Verificar que find se llamó solo con company_id
        mock_transfers_collection.find.assert_called_once_with({"company_id": test_company_id})
        mock_find_result.sort.assert_called_once_with("timestamp", -1)
        mock_cursor.to_list.assert_awaited_once_with(length=None)
        assert result == mock_result_list

    @pytest.mark.asyncio
    async def test_fetch_transfers_by_filters_all_filters(self, mocker):
        """Prueba fetch_transfers_by_filters con todos los filtros aplicados."""
        test_company_id = "comp_filter_2"
        start_dt = datetime(2024, 3, 10, 0, 0, 0)
        end_dt = datetime(2024, 3, 20, 0, 0, 0)
        bank_p = "1234"
        min_a = 50.0
        max_a = 500.0
        mock_result_list = [{"_id": ObjectId(), "amount": 150}]

        # Mockear find().sort().to_list()
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_result_list)
        mock_find_result = MagicMock()
        mock_find_result.sort = MagicMock(return_value=mock_cursor)
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.find = MagicMock(return_value=mock_find_result)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)
        # Mockear timezone.utc para predictibilidad (si no se importó directamente)
        # mocker.patch(f"{MODULE_PATH}.timezone.utc", timezone.utc)

        result = await fetch_transfers_by_filters(
            company_id=test_company_id,
            start_date=start_dt,
            end_date=end_dt,
            bank_prefix=bank_p,
            min_amount=min_a,
            max_amount=max_a
        )

        # Verificar query construida
        expected_query = {
            "company_id": test_company_id,
            "timestamp": {
                # Esperamos que las fechas se hagan conscientes de UTC y end_date ajustada
                "$gte": start_dt.replace(tzinfo=timezone.utc),
                "$lte": end_dt.replace(tzinfo=timezone.utc, hour=23, minute=59, second=59, microsecond=999999)
            },
            "from_account": {"$regex": f"^.{{4}}{bank_p}"},
            "amount": {"$gte": min_a, "$lte": max_a}
        }
        mock_transfers_collection.find.assert_called_once()
        call_args, _ = mock_transfers_collection.find.call_args
        actual_query = call_args[0]
        # Comparamos campo por campo por los datetimes
        assert actual_query["company_id"] == expected_query["company_id"]
        assert abs(actual_query["timestamp"]["$gte"] - expected_query["timestamp"]["$gte"]) < timedelta(seconds=1)
        assert abs(actual_query["timestamp"]["$lte"] - expected_query["timestamp"]["$lte"]) < timedelta(seconds=1)
        assert actual_query["from_account"] == expected_query["from_account"]
        assert actual_query["amount"] == expected_query["amount"]

        mock_find_result.sort.assert_called_once_with("timestamp", -1)
        mock_cursor.to_list.assert_awaited_once_with(length=None)
        assert result == mock_result_list

    @pytest.mark.asyncio
    async def test_fetch_transfers_by_filters_invalid_bank_prefix(self, mocker):
        """Prueba que un bank_prefix inválido no se aplica y se loguea warning."""
        test_company_id = "comp_filter_3"
        invalid_bank_prefix = "ABCD" # No es dígito
        mock_result_list = [{"_id": ObjectId()}]

        # Mockear find().sort().to_list()
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_result_list)
        mock_find_result = MagicMock()
        mock_find_result.sort = MagicMock(return_value=mock_cursor)
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.find = MagicMock(return_value=mock_find_result)
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)
        # Mockear el logger para verificar el warning
        mock_log = mocker.patch(f"{MODULE_PATH}.log")

        result = await fetch_transfers_by_filters(
            company_id=test_company_id,
            bank_prefix=invalid_bank_prefix
        )

        # Verificar que el filtro de banco NO se aplicó
        expected_query = {"company_id": test_company_id} # Solo company_id
        mock_transfers_collection.find.assert_called_once_with(expected_query)
        # Verificar que se llamó al logger warning
        mock_log.warning.assert_called_once_with(
            f"[DB Table] Invalid bank_prefix format received: '{invalid_bank_prefix}'. Filter not applied."
        )
        assert result == mock_result_list

    # (Puedes añadir más tests para otras combinaciones de filtros si quieres más detalle)

    # --- Pruebas para fetch_dashboard_data_internal ---
    # Probaremos principalmente la construcción del query y que se llamen las agregaciones

    @pytest.mark.asyncio
    async def test_fetch_dashboard_data_internal_no_filters(self, mocker):
        """Prueba fetch_dashboard_data_internal sin filtros."""
        test_company_id = "comp_dash_1"

        # Mockear llamadas a BD (aggregate y distinct)
        # Necesitamos 5 resultados de aggregate + 1 de distinct
        mock_agg_cursor_summary = MagicMock()
        mock_agg_cursor_summary.to_list = AsyncMock(return_value=[{"totalTransactions": 10, "totalAnomalies": 1, "totalAmount": 1000.0}])
        mock_agg_cursor_volume = MagicMock()
        mock_agg_cursor_volume.to_list = AsyncMock(return_value=[{"date": "2024-01-15", "count": 5}])
        mock_agg_cursor_anom_volume = MagicMock()
        mock_agg_cursor_anom_volume.to_list = AsyncMock(return_value=[{"date": "2024-01-15", "count": 1}])
        mock_agg_cursor_status = MagicMock()
        mock_agg_cursor_status.to_list = AsyncMock(return_value=[{"status": "completada", "count": 9}, {"status": "pendiente", "count": 1}])
        mock_agg_cursor_amount = MagicMock()
        mock_agg_cursor_amount.to_list = AsyncMock(return_value=[{"year": 2024, "month": 1, "amount": 1000.0}])
        mock_distinct_result = ["ACC1", "ACC2"]

        mock_transfers_collection = MagicMock()
        # Usar side_effect para devolver diferentes cursores en orden
        mock_transfers_collection.aggregate = MagicMock(side_effect=[
            mock_agg_cursor_summary,
            mock_agg_cursor_volume,
            mock_agg_cursor_anom_volume,
            mock_agg_cursor_status,
            mock_agg_cursor_amount
        ])
        mock_transfers_collection.distinct = AsyncMock(return_value=mock_distinct_result) # distinct es async
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        # Llamar a la función
        result_data = await fetch_dashboard_data_internal(company_id=test_company_id)

        # Verificaciones principales
        assert mock_transfers_collection.aggregate.call_count == 5
        mock_transfers_collection.distinct.assert_awaited_once()

        # Verificar el query base usado en la PRIMERA agregación y en distinct
        expected_base_query = {"company_id": test_company_id}
        first_agg_call_args, _ = mock_transfers_collection.aggregate.call_args_list[0]
        first_agg_pipeline = first_agg_call_args[0]
        assert first_agg_pipeline[0]["$match"] == expected_base_query # Verificar $match de la primera pipeline

        distinct_call_args, _ = mock_transfers_collection.distinct.await_args
        assert distinct_call_args[0] == "from_account" # Field
        assert distinct_call_args[1] == expected_base_query # Filter query

        # Verificar estructura general del resultado y algunos valores clave
        assert "summary" in result_data
        assert "volumeByDay" in result_data
        assert "anomalousVolumeByDay" in result_data
        assert "statusDistribution" in result_data
        assert "amountByMonth" in result_data
        assert result_data["summary"]["totalTransactions"] == 10
        assert result_data["summary"]["totalAnomalies"] == 1
        assert result_data["summary"]["totalAmount"] == 1000.0
        assert result_data["summary"]["newSenders"] == 2
        assert result_data["volumeByDay"] == [{"date": "2024-01-15", "count": 5}]
        # Los summaries P y PA no se calculan en el código, así que estarán con valores default
        assert result_data["summaryPreviousMonth"] == {"totalTransfers": 0, "totalAnomalies": 0, "totalAmount": 0.0}
        assert result_data["summaryMonthBeforePrevious"] == {"totalTransfers": 0, "totalAnomalies": 0, "totalAmount": 0.0}


    @pytest.mark.asyncio
    async def test_fetch_dashboard_data_internal_with_filters(self, mocker):
        """Prueba fetch_dashboard_data_internal con algunos filtros."""
        test_company_id = "comp_dash_2"
        start_dt = datetime(2024, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
        max_a = 1000.0

        # Mockear llamadas a BD (solo necesitamos verificar la query en la primera llamada)
        mock_agg_cursor = MagicMock()
        mock_agg_cursor.to_list = AsyncMock(return_value=[]) # Devolver vacío para simplificar
        mock_transfers_collection = MagicMock()
        mock_transfers_collection.aggregate = MagicMock(return_value=mock_agg_cursor)
        mock_transfers_collection.distinct = AsyncMock(return_value=[])
        mocker.patch(f"{MODULE_PATH}.db.transfers", mock_transfers_collection)

        # Llamar a la función
        await fetch_dashboard_data_internal(
            company_id=test_company_id,
            start_date=start_dt,
            max_amount=max_a
        )

        # Verificar el query construido en la PRIMERA agregación y en distinct
        expected_query = {
            "company_id": test_company_id,
            "timestamp": {"$gte": start_dt},
            "amount": {"$lte": max_a}
        }
        # Verificar primera llamada a aggregate
        assert mock_transfers_collection.aggregate.call_count > 0 # Se llamó al menos una vez
        first_agg_call_args, _ = mock_transfers_collection.aggregate.call_args_list[0]
        first_agg_pipeline = first_agg_call_args[0]
        # Comparamos $match campo por campo
        assert first_agg_pipeline[0]["$match"]["company_id"] == expected_query["company_id"]
        assert first_agg_pipeline[0]["$match"]["amount"] == expected_query["amount"]
        assert abs(first_agg_pipeline[0]["$match"]["timestamp"]["$gte"] - expected_query["timestamp"]["$gte"]) < timedelta(seconds=1)

        # Verificar llamada a distinct
        mock_transfers_collection.distinct.assert_awaited_once()
        distinct_call_args, _ = mock_transfers_collection.distinct.await_args
        assert distinct_call_args[0] == "from_account"
        # Comparamos query de distinct campo por campo
        assert distinct_call_args[1]["company_id"] == expected_query["company_id"]
        assert distinct_call_args[1]["amount"] == expected_query["amount"]
        assert abs(distinct_call_args[1]["timestamp"]["$gte"] - expected_query["timestamp"]["$gte"]) < timedelta(seconds=1)