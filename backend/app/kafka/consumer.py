from confluent_kafka import Consumer
import json
from datetime import datetime
import asyncio
import pandas as pd
import joblib
from app.database import db

# Cargar el modelo Isolation Forest
model = joblib.load("isolation_forest.pkl")

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

        # Validar y convertir timestamp
        if "timestamp" in transfer:
            if isinstance(transfer["timestamp"], str):
                transfer["timestamp"] = datetime.fromisoformat(transfer["timestamp"])
            elif not isinstance(transfer["timestamp"], datetime):
                raise ValueError(f"Formato de timestamp no soportado: {transfer['timestamp']}")

        # Convertir timestamp a segundos desde el inicio del año
        timestamp_sec = (transfer["timestamp"] - datetime(2025, 1, 1)).total_seconds()

        # Convertir estado a número
        status_numeric = status_mapping.get(transfer["status"], -1)

        # Crear DataFrame con la transacción para el modelo
        data = pd.DataFrame([[transfer["amount"], timestamp_sec, status_numeric]], 
                            columns=["amount", "timestamp", "status"])

        # Predecir anomalía (Isolation Forest devuelve -1 para anomalías)
        prediction = model.predict(data)
        is_anomalous = prediction[0] == -1

        # Agregar flag de anomalía en la transferencia
        transfer["is_anomalous"] = is_anomalous

        # Insertar en la base de datos
        inserted = await db.transfers.insert_one(transfer)
        transfer["_id"] = inserted.inserted_id

        if is_anomalous:
            print(f"⚠️ ALERTA: Transacción anómala detectada: {transfer}")

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
