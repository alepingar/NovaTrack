import pandas as pd
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

df["amount_mean"] = df.groupby("company_id")["amount"].transform("mean")
df["amount_std"] = df.groupby("company_id")["amount"].transform("std")

df["amount_zscore"] = (df["amount"] - df["amount_mean"]) / df["amount_std"]

# Convertir estado de la transferencia a valores numéricos
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
df["status"] = df["status"].map(status_mapping)

df["hour"] = df["timestamp"].dt.hour
# Seleccionar columnas finales
features = ["amount_zscore","status"]
X = df[features]

# Guardar los datos preprocesados en CSV para entrenar el modelo
X.to_csv("preprocessed_data.csv", index=False)
print("Datos preprocesados guardados en 'preprocessed_data.csv'")
