
import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock, ANY
import pandas as pd
import numpy as np
import os

import app.kafka.consumer as consumer_module
from app.kafka.consumer import process_message, company_stats


# --- Helper para crear mensajes Kafka simulados ---
def create_mock_kafka_message(payload_dict):
    msg = MagicMock()
    # El método value() debe devolver bytes codificados en utf-8
    msg.value.return_value = json.dumps(payload_dict).encode('utf-8')
    msg.error.return_value = None # Simular mensaje sin error Kafka
    return msg

# --- Clase de Pruebas ---
@pytest.mark.usefixtures("mocker") # Para usar mocker en métodos de clase si es necesario
class TestKafkaConsumer:

    # Módulo a parchear (el archivo consumidor)
    MODULE_PATH = "app.kafka.consumer"

    # Ejemplo de datos de compañía para las estadísticas (puedes ajustar)
    sample_company_id = "comp-integrated-test"
    sample_stats = {
        "mean": 150.0,
        "std": 50.0,
        "q5": 80.0,
        "q95": 220.0
    }

    # Configuración común de mocks para varias pruebas
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker):
        # Mockear colección de transferencias (global en el módulo consumidor)
        self.mock_transfers_collection = AsyncMock()
        # Configurar mocks por defecto para los métodos usados
        self.mock_transfers_collection.count_documents = AsyncMock(return_value=100) # Asumir > 30 por defecto
        self.mock_transfers_collection.insert_one = AsyncMock()
        # Mockear aggregate usado por get_recurrent_clients
        mock_agg_cursor = MagicMock()
        mock_agg_cursor.to_list = AsyncMock(return_value=[]) # Sin recurrentes por defecto
        self.mock_transfers_collection.aggregate = MagicMock(return_value=mock_agg_cursor)
        # Mockear find usado por fetch_company_stats_for_company (si se llama)
        mock_find_cursor = MagicMock()
        mock_find_cursor.to_list = AsyncMock(return_value=[]) # Sin datos por defecto
        self.mock_transfers_collection.find = MagicMock(return_value=mock_find_cursor)

        mocker.patch(f"{self.MODULE_PATH}.transfers_collection", self.mock_transfers_collection)

        # Mockear get_recurrent_clients y fetch_company_stats_for_company
        self.mock_get_recurrent = AsyncMock(return_value=set()) # Sin recurrentes por defecto
        mocker.patch(f"{self.MODULE_PATH}.get_recurrent_clients", self.mock_get_recurrent)
        self.mock_fetch_stats = AsyncMock() # No devuelve nada, modifica global
        mocker.patch(f"{self.MODULE_PATH}.fetch_company_stats_for_company", self.mock_fetch_stats)

        # Mockear save_notification
        self.mock_save_notification = AsyncMock()
        mocker.patch(f"{self.MODULE_PATH}.save_notification", self.mock_save_notification)

        # Mockear/Controlar el diccionario global company_stats
        # Lo reseteamos y ponemos datos de prueba para nuestra compañía
        self.mock_company_stats_dict = {self.sample_company_id: self.sample_stats}
        mocker.patch.dict(consumer_module.company_stats, self.mock_company_stats_dict, clear=True)

        # Mockear print para evitar salida en consola (opcional)
        mocker.patch('builtins.print')


    @pytest.mark.asyncio
    async def test_process_message_normal_transfer(self, mocker):
        """
        Valida que una transferencia NORMAL es procesada correctamente
        por el modelo integrado y marcada como is_anomalous=False.
        """
        # Crear datos de transferencia simulada NORMAL
        normal_transfer_data = {
            "id": "normal-123",
            "company_id": self.sample_company_id,
            "amount": 160.0, # Cerca de la media, dentro de q5-q95
            "status": "completada",
            "from_account": "ACC_RECURRENT_A", # Asumir que es recurrente
            "timestamp": datetime.now(timezone.utc).isoformat() # Hora actual
            # Añadir otros campos que pueda tener el mensaje Kafka
        }
        mock_msg = create_mock_kafka_message(normal_transfer_data)

        # Configurar mocks específicos para este caso
        self.mock_get_recurrent.return_value = {"ACC_RECURRENT_A"} # Hacerla recurrente

        # Llamar a la función a probar
        await process_message(mock_msg)

        # Verificaciones
        self.mock_transfers_collection.count_documents.assert_awaited_once_with({"company_id": self.sample_company_id})
        self.mock_get_recurrent.assert_awaited_once()
        # Verificar que insert_one se llamó
        self.mock_transfers_collection.insert_one.assert_awaited_once()
        # Verificar el documento insertado (especialmente is_anomalous)
        call_args, _ = self.mock_transfers_collection.insert_one.await_args
        inserted_doc = call_args[0]
        assert inserted_doc["id"] == normal_transfer_data["id"]
        assert inserted_doc["is_anomalous"] is False # <-- CLAVE: Debe ser False
        assert isinstance(inserted_doc["timestamp"], datetime) # Verificar conversión

        # Verificar que NO se llamó a save_notification
        self.mock_save_notification.assert_not_awaited()


    @pytest.mark.asyncio
    async def test_process_message_anomalous_transfer(self, mocker):
        """
        Valida que una transferencia ANÓMALA es procesada correctamente
        por el modelo integrado y marcada como is_anomalous=True.
        """
        # Crear datos de transferencia simulada ANÓMALA
        anomalous_transfer_data = {
            "id": "anomaly-456",
            "company_id": self.sample_company_id,
            "amount": 5000.0, # Muy alto (z-score alto, fuera de q95)
            "status": "completada",
            "from_account": "ACC_NEW_SENDER_XYZ", # Asumir que NO es recurrente
            "timestamp": datetime.now(timezone.utc).replace(hour=3).isoformat() # Hora "rara" (3 AM)
            # Añadir otros campos que pueda tener el mensaje Kafka
        }
        mock_msg = create_mock_kafka_message(anomalous_transfer_data)

        # Configurar mocks específicos (get_recurrent devuelve set vacío)
        self.mock_get_recurrent.return_value = set()

        # Llamar a la función a probar
        await process_message(mock_msg)

        # Verificaciones
        self.mock_transfers_collection.count_documents.assert_awaited_once_with({"company_id": self.sample_company_id})
        self.mock_get_recurrent.assert_awaited_once()
        self.mock_transfers_collection.insert_one.assert_awaited_once()
        call_args, _ = self.mock_transfers_collection.insert_one.await_args
        inserted_doc = call_args[0]
        assert inserted_doc["id"] == anomalous_transfer_data["id"]
        assert inserted_doc["is_anomalous"] is True
        assert isinstance(inserted_doc["timestamp"], datetime)

        # Verificar que SÍ se llamó a save_notification
        self.mock_save_notification.assert_awaited_once() # Correcto

        # 1. Captura args Y kwargs
        notif_call_args, notif_call_kwargs = self.mock_save_notification.await_args

        # 2. Verifica args posicionales
        assert "anómala" in notif_call_args[0] # Verificar mensaje (índice 0)
        assert notif_call_args[1] == "Anomalía" # Verificar tipo (índice 1)

        # 3. Verifica kwargs
        assert "company_id" in notif_call_kwargs # Asegurar que la clave está
        assert notif_call_kwargs["company_id"] == self.sample_company_id # Verificar company_id en kwargs


    @pytest.mark.asyncio
    async def test_process_message_less_than_30_transfers(self, mocker):
        """
        Valida que si hay menos de 30 transferencias, se marca como normal sin llamar al modelo.
        """
        # Datos de cualquier transferencia
        transfer_data = { "id": "lowhist-789", "company_id": self.sample_company_id, "amount": 100.0, "status": "completada", "from_account": "ACC_ANY", "timestamp": datetime.now(timezone.utc).isoformat() }
        mock_msg = create_mock_kafka_message(transfer_data)

        # Mockear count_documents para devolver < 30
        self.mock_transfers_collection.count_documents = AsyncMock(return_value=25)

        # Mockear el método del modelo para asegurar que NO se llama
        mock_score_samples = mocker.patch.object(consumer_module.model, 'score_samples')

        # Llamar a la función a probar
        await process_message(mock_msg)

        # Verificaciones
        self.mock_transfers_collection.count_documents.assert_awaited_once_with({"company_id": self.sample_company_id})
        # Verificar que se insertó como NO anómala
        self.mock_transfers_collection.insert_one.assert_awaited_once()
        call_args, _ = self.mock_transfers_collection.insert_one.await_args
        assert call_args[0]["is_anomalous"] is False
        # Verificar que NO se usó el modelo
        mock_score_samples.assert_not_called()
        self.mock_save_notification.assert_not_awaited()