import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["nova_track"]
transfers_collection = db["transfers"]

async def fetch_data():
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)  # Obtener todos los documentos
    return pd.DataFrame(data)

# Ejecutar la carga de datos
df = asyncio.run(fetch_data())

df = df.sample(frac=1).reset_index(drop=True)
df = df.sort_values(by=["company_id", "timestamp"])

# Calcular estadísticas por empresa
df["amount_mean"] = df.groupby("company_id")["amount"].transform("mean")
df["amount_std"] = df.groupby("company_id")["amount"].transform("std")
df["amount_zscore"] = (df["amount"] - df["amount_mean"]) / df["amount_std"]

# Calcular IQR por empresa
q1 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.05))
q3 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.95))
df["amount_iqr_low"] = q1
df["amount_iqr_high"] = q3

df["is_outside_iqr"] = ((df["amount"] < df["amount_iqr_low"]) | (df["amount"] > df["amount_iqr_high"])).astype(int)

# One-Hot Encoding para la columna 'status'
status_one_hot = pd.get_dummies(df['status'], prefix='status')

# Eliminar la columna original 'status'
df = df.drop(columns=['status'])

# Concatenar las columnas One-Hot al DataFrame
df = pd.concat([df, status_one_hot], axis=1)

df["hour"] = df["timestamp"].dt.hour 

# Seleccionar columnas finales
df['is_recurrent_client'] = 0

# Marcar todos los 'from_account' que aparecen más de una vez como recurrentes
recurrent_accounts = df['from_account'].value_counts()[df['from_account'].value_counts() > 1].index

# Ahora marcamos las transferencias de esos accounts como recurrentes
df.loc[df['from_account'].isin(recurrent_accounts), 'is_recurrent_client'] = 1

# Seleccionar las características para el modelo
features = ["amount_zscore", "is_recurrent_client", "hour", "is_outside_iqr"] + list(status_one_hot.columns)
X = df[features]

# Guardar los datos preprocesados en CSV para entrenar el modelo
X.to_csv("preprocessed_data.csv", index=False)
print("Datos preprocesados guardados en 'preprocessed_data.csv'")
print(df.isnull().sum())
