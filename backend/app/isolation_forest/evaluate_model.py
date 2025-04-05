import pandas as pd
import numpy as np
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sklearn.preprocessing import MinMaxScaler
import joblib

# Cargar el modelo
model_path = "isolation_forest.pkl"
if os.path.exists(model_path):
    model = joblib.load(model_path)
    print("Modelo cargado correctamente.")
else:
    print(f"El modelo no se encuentra en la ruta: {model_path}")

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["nova_track"]
transfers_collection = db["transfers"]

# Función para obtener los datos desde MongoDB
async def fetch_data():
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)
    return pd.DataFrame(data)

# Cargar los datos
df = asyncio.run(fetch_data())

# Preprocesar los datos
df["amount_log"] = np.log1p(df["amount"])

# Guardar min y max antes de escalar
amount_log_min = df["amount_log"].min()
amount_log_max = df["amount_log"].max()

scaler = MinMaxScaler()
df["amount_scaled"] = scaler.fit_transform(df[["amount_log"]])

# Guardar min y max en un archivo JSON
scaler_params = {
    "amount_log_min": float(amount_log_min),
    "amount_log_max": float(amount_log_max)
}

SCALER_PARAMS_PATH = os.path.join(os.getcwd(), "scaler_params.json")
with open(SCALER_PARAMS_PATH, "w") as f:
    json.dump(scaler_params, f)

print(f"Parámetros de escalado guardados en {SCALER_PARAMS_PATH}")

# Convertir estado de la transferencia en valores numéricos
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
df["status"] = df["status"].map(status_mapping)

# Seleccionar las características para la predicción
features = ["amount_scaled", "status"]
X = df[features]

# Hacer las predicciones (1: normal, -1: anómala)
predictions = model.predict(X)

# Convertir las predicciones a formato binario (1: normal, 0: anómala)
predictions = (predictions == -1).astype(int)

# Obtener las etiquetas reales de anomalías desde la base de datos (campo 'is_anomalous')
real_labels = df['is_anomalous'].values

# Calcular el porcentaje de aciertos
correct_predictions = (predictions == real_labels).sum()
total_predictions = len(df)
accuracy = correct_predictions / total_predictions * 100

print(f"Porcentaje de aciertos: {accuracy:.2f}%")
