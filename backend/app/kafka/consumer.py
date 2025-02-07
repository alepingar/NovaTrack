from confluent_kafka import Consumer
import json
from datetime import datetime
from app.database import db
import asyncio
from app.services.ml_anomaly_detector import analyze_transaction  

# Configuración del consumidor
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'transfer_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}
consumer = Consumer(consumer_config)

async def process_message(msg):
    """
    Procesa un mensaje del consumidor, lo analiza con ML y lo guarda en la base de datos.
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

        # Insertar en la base de datos
        inserted = await db.transfers.insert_one(transfer)

        # Agregar ID a la transacción
        transfer["_id"] = inserted.inserted_id

        # Analizar con el modelo de Machine Learning
        is_anomalous = await analyze_transaction(transfer)

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
