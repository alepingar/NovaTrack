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
q1 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.25))
q3 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.75))
df["amount_iqr_low"] = q1
df["amount_iqr_high"] = q3

df["is_outside_iqr"] = ((df["amount"] < df["amount_iqr_low"]) | (df["amount"] > df["amount_iqr_high"])).astype(int)

status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
df["status"] = df["status"].map(status_mapping)

df["hour"] = df["timestamp"].dt.hour 

# Seleccionar columnas finales
df['is_recurrent_client'] = 0

# Marcar todos los 'from_account' que aparecen más de una vez como recurrentes
recurrent_accounts = df['from_account'].value_counts()[df['from_account'].value_counts() > 1].index

# Ahora marcamos las transferencias de esos accounts como recurrentes
df.loc[df['from_account'].isin(recurrent_accounts), 'is_recurrent_client'] = 1
    
features = ["amount_zscore", "is_outside_iqr","status","is_recurrent_client","hour"]
X = df[features]

# Guardar los datos preprocesados en CSV para entrenar el modelo
X.to_csv("preprocessed_data.csv", index=False)
print("Datos preprocesados guardados en 'preprocessed_data.csv'")
print(df.isnull().sum())
