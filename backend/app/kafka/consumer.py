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

# Cargar el modelo con la ruta absoluta
model = joblib.load(MODEL_PATH)

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

# Diccionario para almacenar estadísticas de cada empresa
company_stats = {}

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

async def fetch_company_stats():
    """
    Obtiene la media y desviación estándar de los montos por cada empresa desde la base de datos.
    """

    # Cargar todas las transferencias en un DataFrame
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)
    df = pd.DataFrame(data)

    if df.empty:
        print("⚠️ No hay datos en la base de datos.")
        return

    # Calcular media y desviación estándar por empresa
    company_stats_df = df.groupby("company_id")["amount"].agg(["mean", "std"]).reset_index()
    
    # Guardar en un diccionario
    global company_stats
    company_stats = company_stats_df.set_index("company_id").to_dict(orient="index")
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

        # Convertir estado a número
        status_numeric = status_mapping.get(transfer["status"], -1)
        # Obtener media y std de la empresa
        company_data = company_stats.get(company_id, {"mean": 0, "std": 1})
        amount_mean = company_data["mean"]
        amount_std = company_data["std"] if company_data["std"] > 0 else 1  # Evitar división por 0

        # Calcular Z-score
        amount_zscore = (amount - amount_mean) / amount_std
        
        is_banking_hour = transfer["timestamp"].hour 
        is_banking_hour = 1 if (8 <= is_banking_hour < 22) else 0
        # Crear DataFrame con las características necesarias para el modelo
        data = pd.DataFrame([[is_banking_hour,amount_zscore, status_numeric]], 
                            columns=["is_banking_hour","amount_zscore", "status"])

        # Predecir anomalía (Isolation Forest devuelve -1 para anomalías)
        prediction = model.predict(data)
        is_anomalous = bool(prediction[0] == -1)

        # Agregar flag de anomalía en la transferencia
        transfer["is_anomalous"] = is_anomalous
        transfer["features"] = {
                "is_banking_hour": is_banking_hour,
                "amount_zscore": amount_zscore,
                "status": status_numeric
            }
        inserted = await db.transfers.insert_one(transfer)
        transfer["_id"] = inserted.inserted_id

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
