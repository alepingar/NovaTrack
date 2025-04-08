from confluent_kafka import Consumer
import json
from datetime import datetime, timezone
import asyncio
import pandas as pd
import joblib
import os
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient 
from app.services.notification_services import save_notification

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
consumer = Consumer(consumer_config)

# Mapeo de estado de transferencias
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}

# Diccionario para almacenar estadísticas de cada empresa
company_stats = {}

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["nova_track"]
transfers_collection = db["transfers"]

async def fetch_company_stats():
    """
    Obtiene la media, desviación estándar, Q1 y Q3 de los montos por cada empresa desde la base de datos.
    """
    # Cargar todas las transferencias en un DataFrame
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)
    df = pd.DataFrame(data)

    if df.empty:
        print("⚠️ No hay datos en la base de datos.")
        return

    # Calcular media, desviación estándar, Q1 y Q3 por empresa
    global company_stats
    company_stats = {}  # Reiniciar el diccionario antes de recalcular las estadísticas
    
    for company_id, group in df.groupby('company_id'):
        q1 = group['amount'].quantile(0.25)
        q3 = group['amount'].quantile(0.75)
        company_stats[company_id] = {
            "mean": group['amount'].mean(),
            "std": group['amount'].std(),
            "q1": q1,
            "q3": q3
        }
    
    print("📊 Estadísticas de empresas cargadas.")
    print(company_stats)

async def process_message(msg):
    """
    Procesa un mensaje del consumidor, lo analiza con Isolation Forest y lo guarda en la base de datos.
    """
    try:
        transfer = json.loads(msg.value().decode('utf-8'))
        print(f"Valor de timestamp recibido: {transfer.get('timestamp')}")

        company_id = transfer.get("company_id")
        amount = transfer.get("amount", 0)

        # Validar y convertir timestamp de la transferencia
        if "timestamp" in transfer:
            if isinstance(transfer["timestamp"], str):
                transfer["timestamp"] = datetime.fromisoformat(transfer["timestamp"])
            elif not isinstance(transfer["timestamp"], datetime):
                raise ValueError(f"Formato de timestamp no soportado: {transfer['timestamp']}")

        # Convertir el timestamp de la transferencia a UTC si no tiene zona horaria
        if transfer["timestamp"].tzinfo is None:
            transfer["timestamp"] = transfer["timestamp"].replace(tzinfo=timezone.utc)

        # Obtener media y std de la empresa
        # Obtener media, std, Q1 y Q3 de la empresa
        company_data = company_stats.get(company_id, {"mean": 0, "std": 1, "q1": 0, "q3": 0})
        amount_mean = company_data["mean"]
        amount_std = company_data["std"] if company_data["std"] > 0 else 1  # Evitar división por 0
        q1 = company_data["q1"]
        q3 = company_data["q3"]

        # Calcular Z-score
        amount_zscore = (amount - amount_mean) / amount_std
        
        # Calcular IQR y si el monto está fuera del rango intercuartil
        is_outside_iqr = 1 if (amount < q1 or amount > q3) else 0

        # Extraer hora del timestamp
        hour = transfer["timestamp"].hour

        status_numeric = status_mapping.get(transfer["status"], -1)
        # Verificar si la cuenta es recurrente
        recurrent_accounts = transfers_collection.aggregate([
            {"$group": {"_id": "$from_account", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ])
        recurrent_accounts = {account["_id"] for account in await recurrent_accounts.to_list(length=None)}
        is_recurrent_client = 1 if transfer["from_account"] in recurrent_accounts else 0

        # Crear DataFrame con las características necesarias para el modelo
        data = pd.DataFrame([[amount_zscore,is_outside_iqr, status_numeric, is_recurrent_client,hour]], 
                            columns=["amount_zscore", "is_outside_iqr","status","is_recurrent_client","hour"])

        # Predecir anomalía (Isolation Forest devuelve -1 para anomalías)
        prediction = model.predict(data)
        is_anomalous = bool(prediction[0] == -1)

        # Agregar flag de anomalía en la transferencia
        transfer["is_anomalous"] = is_anomalous

        if is_anomalous:
            print(f"⚠️ ALERTA: Transacción anómala detectada: {transfer}")
            message = f"⚠️ Alerta: Se detectó una transferencia anómala con ID: {transfer['id']}"
        else:
            print(f"✅ Transacción normal: {transfer}")

    except Exception as e:
        print(f"Error procesando el mensaje: {e}")

async def consume_transfers():
    """
    Función asíncrona para consumir transferencias desde Kafka y analizar cada una.
    """
    try:
        await fetch_company_stats()  # Obtener estadísticas antes de empezar
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
