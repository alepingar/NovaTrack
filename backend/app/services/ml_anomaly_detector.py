import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from app.database import db
from app.routes.notification_routes import active_connections

async def notify_anomaly(transaction):
    """
    Notifica a todos los clientes conectados sobre una nueva anomalía.
    """
    for connection in active_connections:
        await connection.send_json(transaction)

def convert_numpy_types(value):
    """Convierte tipos de datos numpy a sus equivalentes en Python."""
    if isinstance(value, (np.bool_, np.bool)):
        return bool(value)
    elif isinstance(value, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(value)
    elif isinstance(value, (np.float16, np.float32, np.float64)):
        return float(value)
    return value  # Retorna el valor original si no es de tipo numpy

async def analyze_transaction(transfer: dict):
    """
    Analiza una transferencia en tiempo real y la marca como anómala si es necesario.
    """
    try:
        features = ["amount", "transaction_fee"]

        # Si hay datos nulos, la transacción no se analiza
        if any(key not in transfer or transfer[key] is None for key in features):
            return False

        df = pd.DataFrame([transfer])
        df_filtered = (df[features] - df[features].mean()) / df[features].std()

        model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        df_filtered["anomaly_score"] = model.fit_predict(df_filtered)

        # 🔥 Convertimos np.bool_ a bool antes de guardarlo
        is_anomalous = bool(df_filtered["anomaly_score"].iloc[0] == -1)

        # 🔥 Convertimos todos los valores de la transacción para evitar errores con MongoDB
        transfer_cleaned = {key: convert_numpy_types(value) for key, value in transfer.items()}

        # Guardar en la base de datos
        await db.transfers.update_one(
            {"_id": transfer_cleaned["_id"]}, 
            {"$set": {"is_anomalous": is_anomalous}}
        )

        return is_anomalous
    except Exception as e:
        print(f"Error al analizar la transacción: {e}")
        return False
