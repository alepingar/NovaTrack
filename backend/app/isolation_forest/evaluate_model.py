import pandas as pd
import joblib
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

model_path = "isolation_forest.pkl"

if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("Modelo cargado correctamente.")
else:
    print(f"El modelo no se encuentra en la ruta: {model_path}")

# Conexión a MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

# Función para cargar datos desde MongoDB
async def fetch_data():
    cursor = transfers_collection.find({})
    data = await cursor.to_list(None)  # Traer todos los datos
    return pd.DataFrame(data)

# Cargar los datos preprocesados desde MongoDB
df = asyncio.run(fetch_data())

# Preprocesar los datos como lo hiciste anteriormente
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Nuevas features necesarias
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek
df = df.sort_values(by=["company_id", "timestamp"])  # Ordenar por empresa y tiempo
df["time_since_last"] = df.groupby("company_id")["timestamp"].diff().dt.total_seconds()
df["time_since_last"] = df["time_since_last"].fillna(df["time_since_last"].median())

# Calcular 7d_transfer_count
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ✅ Ordenar por empresa y tiempo
df = df.sort_values(by=["company_id", "timestamp"])

# ✅ Calcular el número de transferencias en los últimos 7 días por empresa
df["7d_transfer_count"] = df.groupby("company_id", group_keys=False).apply(
    lambda x: x.set_index("timestamp").rolling("7D", min_periods=1).count()["amount"]
).reset_index(drop=True)

# Estadísticas de monto por empresa
df["mean_amount"] = df.groupby("company_id")["amount"].transform("mean")
df["std_amount"] = df.groupby("company_id")["amount"].transform("std")
df["amount_zscore"] = (df["amount"] - df["mean_amount"]) / df["std_amount"]

# Convertir estado de la transferencia en valores numéricos
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
df["status"] = df["status"].map(status_mapping)

# Seleccionar las características correctas
features = ["amount", "hour", "day_of_week", "time_since_last", "7d_transfer_count", "amount_zscore", "status"]
X = df[features]

# Cargar el modelo entrenado y el scaler guardado
scaler = joblib.load("scaler.pkl")

# Normalizar los datos usando el scaler guardado
X_scaled = scaler.transform(X)

# Hacer las predicciones (1: normal, -1: anómala)
predictions = model.predict(X_scaled)

# Convertir las predicciones a formato binario (1: normal, 0: anómala)
predictions = (predictions == -1).astype(int)

# Obtener las etiquetas reales de anomalías desde la base de datos (campo 'is_anomalous')
real_labels = df['is_anomalous'].values  # Etiquetas reales de anomalías

# Calcular el porcentaje de aciertos
correct_predictions = (predictions == real_labels).sum()
total_predictions = len(df)
accuracy = correct_predictions / total_predictions * 100
print(f"Porcentaje de aciertos: {accuracy:.2f}%")
