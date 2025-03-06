from confluent_kafka import Consumer
import json
from datetime import datetime, timezone
import asyncio
import pandas as pd
import joblib
import os
import numpy as np

from app.services.notification_services import save_notification

# Obtener la ruta absoluta del directorio actual
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Definir la ruta del modelo dentro de la misma carpeta
MODEL_PATH = os.path.join(CURRENT_DIR, "../isolation_forest/isolation_forest.pkl")

# Cargar el modelo con la ruta absoluta
model = joblib.load(MODEL_PATH)

# Ruta del archivo con los valores de min y max para normalización
SCALER_PARAMS_PATH = os.path.join(CURRENT_DIR, "../isolation_forest/scaler_params.json")

# Cargar los valores de min y max desde el preprocesamiento
with open(SCALER_PARAMS_PATH, "r") as f:
    scaler_params = json.load(f)
amount_log_min = scaler_params["amount_log_min"]
amount_log_max = scaler_params["amount_log_max"]

# Configuración del consumidor Kafka
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'transfer_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}
consumer = Consumer(consumer_config)

# Mapeo de estado de transferencias
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}

async def process_message(msg):
    """
    Procesa un mensaje del consumidor, lo analiza con Isolation Forest y lo guarda en la base de datos.
    """
    try:
        transfer = json.loads(msg.value().decode('utf-8'))
        print(f"Valor de timestamp recibido: {transfer.get('timestamp')}")

        # Validar y convertir timestamp de la transferencia
        if "timestamp" in transfer:
            if isinstance(transfer["timestamp"], str):
                transfer["timestamp"] = datetime.fromisoformat(transfer["timestamp"])
            elif not isinstance(transfer["timestamp"], datetime):
                raise ValueError(f"Formato de timestamp no soportado: {transfer['timestamp']}")

        # Convertir el timestamp de la transferencia a UTC si no tiene zona horaria
        if transfer["timestamp"].tzinfo is None:
            transfer["timestamp"] = transfer["timestamp"].replace(tzinfo=timezone.utc)

        # Convertir estado a número
        status_numeric = status_mapping.get(transfer["status"], -1)

        # Aplicar log1p a amount (como en preprocesamiento)
        amount_log = np.log1p(transfer["amount"])

        # Aplicar MinMaxScaler manualmente con los valores guardados
        amount_scaled = (amount_log - amount_log_min) / (amount_log_max - amount_log_min)

        print(f"🔹 Amount original: {transfer['amount']}, Log: {amount_log}, Scaled: {amount_scaled}")

        # Crear DataFrame con las características necesarias para el modelo
        data = pd.DataFrame([[amount_scaled, status_numeric]], 
                            columns=["amount_scaled", "status"])

        # Predecir anomalía (Isolation Forest devuelve -1 para anomalías)
        prediction = model.predict(data)
        is_anomalous = bool(prediction[0] == -1)

        # Agregar flag de anomalía en la transferencia
        transfer["is_anomalous"] = is_anomalous

        if is_anomalous:
            print(f"⚠️ ALERTA: Transacción anómala detectada: {transfer}")
            message = f"⚠️ Alerta: Se detectó una transferencia anómala con ID: {transfer['id']}"
            await save_notification(message, "Anomalía",company_id=transfer["company_id"])
        else:
            print(f"✅ Transacción normal: {transfer}")

    except Exception as e:
        print(f"Error procesando el mensaje: {e}")

async def consume_transfers():
    """
    Función asíncrona para consumir transferencias desde Kafka y analizar cada una.
    """
    try:
        consumer.subscribe(['transfers'])
        print("Esperando transferencias...")

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                await asyncio.sleep(2)  
                continue
            if msg.error():
                print(f"Error en mensaje: {msg.error()}")
            else:
                await process_message(msg)
    finally:
        consumer.close()

if __name__ == "__main__":
    asyncio.run(consume_transfers())
