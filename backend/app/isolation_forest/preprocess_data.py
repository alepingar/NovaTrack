import pandas as pd
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Conexión a MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

async def fetch_data():
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)  # Obtener todos los documentos
    return pd.DataFrame(data)

# Ejecutar la carga de datos
df = asyncio.run(fetch_data())

# Convertir timestamp a datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Nueva feature: Hora del día
df["hour"] = df["timestamp"].dt.hour

# Nueva feature: Día de la semana (0=Lunes, 6=Domingo)
df["day_of_week"] = df["timestamp"].dt.dayofweek

# Nueva feature: Tiempo desde la última transferencia de la empresa
df = df.sort_values(by=["company_id", "timestamp"])  # Ordenar por empresa y tiempo
df["time_since_last"] = df.groupby("company_id")["timestamp"].diff().dt.total_seconds()
df["time_since_last"] = df["time_since_last"].fillna(0)

df["timestamp"] = pd.to_datetime(df["timestamp"])
# ✅ Ordenar por empresa y tiempo
df = df.sort_values(by=["company_id", "timestamp"])
# ✅ Calcular el número de transferencias en los últimos 7 días por empresa
df["7d_transfer_count"] = df.groupby("company_id", group_keys=False).apply(
    lambda x: x.set_index("timestamp").rolling("7D", min_periods=1).count()["amount"]
).reset_index(level=0, drop=True)

# Nueva feature: Estadísticas de monto por empresa
df["mean_amount"] = df.groupby("company_id")["amount"].transform("mean")
df["std_amount"] = df.groupby("company_id")["amount"].transform("std").fillna(1)
df["amount_zscore"] = (df["amount"] - df["mean_amount"]) / df["std_amount"]

# Convertir estado de la transferencia a valores numéricos
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
df["status"] = df["status"].map(status_mapping)

# Seleccionar columnas finales
features = ["amount", "hour", "day_of_week", "time_since_last", "7d_transfer_count", "amount_zscore", "status"]
X = df[features]

# Guardar los datos preprocesados en CSV para entrenar el modelo
X.to_csv("preprocessed_data.csv", index=False)
print("Datos preprocesados guardados en 'preprocessed_data.csv'")
