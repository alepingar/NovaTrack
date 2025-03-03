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
    data = await cursor.to_list() 
    return pd.DataFrame(data)

# Ejecutar la carga de datos
df = asyncio.run(fetch_data())

# Convertir timestamp a número (segundos desde el inicio del año)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["timestamp"] = (df["timestamp"] - pd.Timestamp("2025-01-01")).dt.total_seconds()

# Convertir estado de la transferencia en valores numéricos
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
df["status"] = df["status"].map(status_mapping)

# Seleccionar solo las columnas numéricas relevantes
features = ["amount", "timestamp", "status"]
X = df[features]

# Guardar los datos preprocesados en CSV para entrenar el modelo
X.to_csv("preprocessed_data.csv", index=False)
print("Datos preprocesados guardados en 'preprocessed_data.csv'")
