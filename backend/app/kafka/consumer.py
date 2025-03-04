from confluent_kafka import Consumer
import json
from datetime import datetime, timezone
import asyncio
import pandas as pd
import joblib
from app.database import db
import os
import numpy as np
# Obtener la ruta absoluta del directorio actual donde está el script
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

async def process_message(msg):
    """
    Procesa un mensaje del consumidor, lo analiza con Isolation Forest y lo guarda en la base de datos.
    """
    try:
        transfer = json.loads(msg.value().decode('utf-8'))
        print(f"Valor de timestamp recibido: {transfer.get('timestamp')}")

        company_id = transfer["company_id"]

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
        status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
        status_numeric = status_mapping.get(transfer["status"], -1)

        # Recuperar las transferencias previas de la misma empresa desde la base de datos
        current_timestamp = transfer["timestamp"]  # Este es el timestamp de la transferencia que estás procesando

        # Obtener las transferencias anteriores a la transferencia actual
        prev_transfers = await db.transfers.find({
            "company_id": company_id,
            "timestamp": {"$lt": current_timestamp}  # Filtrar por timestamp anterior a la transferencia que estás procesando
        }).sort("timestamp", -1).to_list(None)  # Ordenar por timestamp descendente

        # Asegurarse de que los timestamps en las transferencias previas sean offset-aware
        for t in prev_transfers:
            # Si es una cadena, conviértela
            if isinstance(t["timestamp"], str):
                t["timestamp"] = datetime.fromisoformat(t["timestamp"])
            # Si es naive, asigna la zona horaria UTC
            if t["timestamp"].tzinfo is None:
                t["timestamp"] = t["timestamp"].replace(tzinfo=timezone.utc)

        # Calcular la hora del día y el día de la semana de la transferencia actual
        hour = transfer["timestamp"].hour
        day_of_week = transfer["timestamp"].weekday()

        # Calcular el tiempo desde la última transferencia de la misma empresa
        if prev_transfers:
            last_transfer_time = prev_transfers[0]["timestamp"]
            print(f"Última transferencia: {last_transfer_time}")
            print(f"Tiempo actual: {transfer['timestamp']}")
            time_since_last = (transfer["timestamp"] - last_transfer_time).total_seconds()
        else:
            time_since_last = 10000

        # Calcular el número de transferencias en los últimos 7 días
        transfers_in_last_7d = [t for t in prev_transfers if (transfer["timestamp"] - t["timestamp"]).total_seconds() <= 7 * 24 * 3600]
        transfer_count_7d = len(transfers_in_last_7d)

        # Calcular la desviación estándar de los montos (Z-score)
        all_transfers = await db.transfers.find({"company_id": company_id}).to_list(length=None)  # No poner límite

        # Verificar si hay transferencias para esa empresa
        if all_transfers:
            # Extraer los montos de todas las transferencias
            amounts = [t["amount"] for t in all_transfers]
            
            # Calcular la media y desviación estándar de todos los montos de esa empresa
            mean_amount = np.mean(amounts) if amounts else 0
            std_amount = np.std(amounts) if amounts else 1
            
            # Calcular Z-score
            amount_zscore = (transfer["amount"] - mean_amount) / std_amount if std_amount != 0 else 0
        else:
            # Si no hay transferencias para esa empresa, asignar valores por defecto
            mean_amount = 0
            std_amount = 1
            amount_zscore = 0

        print("Valores de características calculados:" + "Ultimo tiempo:" + str(time_since_last) +"media de 7 dais:" + str(transfer_count_7d) + "zAmount:"+ str(amount_zscore))
        # Crear DataFrame con las 7 características necesarias para el modelo
        data = pd.DataFrame([[transfer["amount"], hour, day_of_week, time_since_last, transfer_count_7d, amount_zscore, status_numeric]], 
                            columns=["amount", "hour", "day_of_week", "time_since_last", "7d_transfer_count", "amount_zscore", "status"])

        # Predecir anomalía (Isolation Forest devuelve -1 para anomalías)
        prediction = model.predict(data)
        is_anomalous = bool(prediction[0] == -1)

        # Agregar flag de anomalía en la transferencia
        transfer["is_anomalous"] = is_anomalous

        # Insertar en la base de datos
        inserted = await db.transfers.insert_one(transfer)
        transfer["_id"] = inserted.inserted_id

        if is_anomalous:
            print(f"⚠️ ALERTA: Transacción anómala detectada: {transfer}")
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
