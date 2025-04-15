import time
from confluent_kafka import Consumer
import json
from datetime import datetime, timezone
import asyncio
import pandas as pd
import joblib
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.notification_services import save_notification  # Asegúrate de que esta importación sea correcta para tu proyecto
from confluent_kafka import KafkaException

# Obtener la ruta absoluta del directorio actual
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Definir la ruta del modelo dentro de la misma carpeta
MODEL_PATH = os.path.join(CURRENT_DIR, "../isolation_forest/isolation_forest.pkl")
kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")
# Cargar el modelo con la ruta absoluta
model = joblib.load(MODEL_PATH)

# Configuración del consumidor Kafka
consumer_config = {
    'bootstrap.servers': kafka_broker,
    'group.id': 'transfer_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}


def wait_for_kafka_consumer(max_retries=10, delay=10):
    for i in range(max_retries):
        try:
            consumer = Consumer(consumer_config)
            consumer.list_topics(timeout=5)  # Verifica que Kafka esté listo
            print("✅ Conectado a Kafka como consumidor.")
            return consumer
        except KafkaException as e:
            print(f"⏳ Kafka no disponible aún (intento {i+1}/{max_retries}): {e}. Esperando {delay}s...")
            time.sleep(delay)
    raise Exception("❌ Kafka no está disponible tras varios intentos.")

consumer = wait_for_kafka_consumer()

# Mapeo de estado de transferencias (para las estadísticas iniciales)
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
status_columns = ['status_completada', 'status_fallida', 'status_pendiente'] # Asegúrate de que coincidan con tus datos

# Diccionario para almacenar estadísticas de cada empresa
company_stats = {}

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["nova_track"]
transfers_collection = db["transfers"]

async def fetch_company_stats():
    """
    Obtiene la media, desviación estándar, Q5 y Q95 de los montos por cada empresa desde la base de datos.
    """
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)
    df = pd.DataFrame(data)

    if df.empty:
        print("⚠️ No hay datos en la base de datos.")
        return

    global company_stats
    company_stats = {}
    for company_id, group in df.groupby('company_id'):
        q5 = group['amount'].quantile(0.05)
        q95 = group['amount'].quantile(0.95)
        company_stats[company_id] = {
            "mean": group['amount'].mean(),
            "std": group['amount'].std(),
            "q5": q5,
            "q95": q95
        }
    print("📊 Estadísticas de empresas cargadas.")
    print(company_stats)

async def get_recurrent_clients():
    """
    Obtiene un conjunto de 'from_account' que han aparecido más de una vez.
    """
    pipeline = [
        {"$group": {"_id": "$from_account", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$project": {"_id": 1}}
    ]
    recurrent_accounts_data = await transfers_collection.aggregate(pipeline).to_list(length=None)
    return {item['_id'] for item in recurrent_accounts_data}

async def process_message(msg):
    """
    Procesa un mensaje del consumidor, lo analiza con Isolation Forest y lo guarda en la base de datos con el anomaly score.
    """
    try:
        transfer = json.loads(msg.value().decode('utf-8'))
        print(f"Mensaje recibido: {transfer}")

        company_id = transfer.get("company_id")
        amount = transfer.get("amount", 0)
        status = transfer.get("status")
        from_account = transfer.get("from_account")
        timestamp_raw = transfer.get('timestamp')
        timestamp = None

        # Validar y convertir timestamp de la transferencia
        if timestamp_raw:
            if isinstance(timestamp_raw, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp_raw.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        timestamp = datetime.strptime(timestamp_raw, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                    except ValueError:
                        print(f"⚠️ Formato de timestamp no soportado: {timestamp_raw}")
                        return  # No procesar si el timestamp es inválido
            elif isinstance(timestamp_raw, datetime):
                timestamp = timestamp_raw
            if timestamp and timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            hour = timestamp.hour if timestamp else 0
        else:
            print("⚠️ Advertencia: No se encontró el timestamp en el mensaje.")
            hour = 0

        # Obtener estadísticas de la empresa (asegúrate de que company_stats esté actualizado)
        company_data = company_stats.get(company_id, {"mean": 0, "std": 1, "q5": 0, "q95": 0})
        amount_mean = company_data["mean"]
        amount_std = company_data["std"] if company_data["std"] > 0 else 1
        amount_iqr_low = company_data["q5"]
        amount_iqr_high = company_data["q95"]

        # Calcular Z-score
        amount_zscore = (amount - amount_mean) / amount_std

        # Calcular si está fuera del IQR
        is_outside_iqr = 1 if (amount < amount_iqr_low or amount > amount_iqr_high) else 0

        # Determinar si el cliente es recurrente
        recurrent_clients = await get_recurrent_clients()
        is_recurrent_client = 1 if from_account in recurrent_clients else 0

        # Crear características One-Hot para 'status'
        status_one_hot = pd.Series([0] * len(status_columns), index=status_columns)
        if status in status_mapping:
            status_index = list(status_mapping.keys()).index(status)
            if 0 <= status_index < len(status_columns):
                status_one_hot[status_columns[status_index]] = 1

        # Crear DataFrame con las características para el modelo
        features = {
            "amount_zscore": [amount_zscore],
            "is_recurrent_client": [is_recurrent_client],
            "hour": [hour],
            "is_outside_iqr": [is_outside_iqr],
        }
        features.update(status_one_hot.to_dict())
        data = pd.DataFrame(features)

        # Asegurarse de que el orden de las columnas coincida con el modelo entrenado
        expected_columns = ["amount_zscore", "is_recurrent_client", "hour", "is_outside_iqr"] + status_columns
        data = data.reindex(columns=expected_columns, fill_value=0)

        # Calcular el anomaly score
        anomaly_score = model.score_samples(data)[0]

        # Predecir anomalía basado en el score
        threshold = np.percentile(model.score_samples(pd.DataFrame(np.zeros((1, len(expected_columns))), columns=expected_columns)), 7.5)
        is_anomalous = bool(anomaly_score < threshold)

        # Agregar flag de anomalía y score a la transferencia
        transfer["is_anomalous"] = is_anomalous

        # Guardar la transferencia en la base de datos
        await transfers_collection.insert_one(transfer)

        if is_anomalous:
            print(f"⚠️ ALERTA: Transacción anómala detectada (Score: {anomaly_score:.4f}): {transfer}")
            message = f"⚠️ Alerta: Se detectó una transferencia anómala con ID: {transfer['id']}"
            await save_notification(message, "Anomalía", company_id=transfer['company_id'])
        else:
            print(f"✅ Transacción normal (Score: {anomaly_score:.4f}): {transfer}")

    except Exception as e:
        print(f"Error procesando el mensaje: {e}")
        import traceback
        traceback.print_exc()

async def consume_transfers():
    """
    Función asíncrona para consumir transferencias desde Kafka y analizar cada una.
    """
    try:
        print("Iniciando el consumidor de transferencias...")
        consumer.subscribe(['transfers'])

        while True:
            await fetch_company_stats()  # Recargar las estadísticas de las empresas
            print("📊 Estadísticas de empresas recargadas.")

            # Consumir mensajes durante un cierto período
            consume_until = asyncio.get_event_loop().time() + (60 * 60) # Consumir durante 1 hora
            while asyncio.get_event_loop().time() < consume_until:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    await asyncio.sleep(1)
                    continue
                if msg.error():
                    print(f"Error en mensaje: {msg.error()}")
                else:
                    await process_message(msg)

            print("⏳ Pausando el consumo para recargar estadísticas...")
            await asyncio.sleep(3 * 60)

    finally:
        consumer.close()

if __name__ == "__main__":
    asyncio.run(consume_transfers())