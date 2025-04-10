import pandas as pd
import numpy as np
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sklearn.preprocessing import MinMaxScaler
import joblib
from sklearn.metrics import recall_score, accuracy_score, precision_score, f1_score

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

df['is_recurrent_client'] = 0

df["hour"] = df["timestamp"].dt.hour 

# Marcar todos los 'from_account' que aparecen más de una vez como recurrentes
recurrent_accounts = df['from_account'].value_counts()[df['from_account'].value_counts() > 1].index

# Ahora marcamos las transferencias de esos accounts como recurrentes
df.loc[df['from_account'].isin(recurrent_accounts), 'is_recurrent_client'] = 1
    
features = ["amount_zscore","is_recurrent_client","hour","is_outside_iqr"]+ list(status_one_hot.columns)
X = df[features]

# Hacer las predicciones (1: normal, -1: anómala)
anomaly_scores = model.score_samples(X)

# Normalizar los anomaly scores a un rango 0-1 para interpretación más clara
scaler = MinMaxScaler()
normalized_scores = scaler.fit_transform(anomaly_scores.reshape(-1, 1))

# Agregar los scores al DataFrame
df["anomaly_score"] = normalized_scores

# Evaluar el rendimiento si aún quieres usar etiquetas binarias
threshold = np.percentile(anomaly_scores, 7.5)  # Por ejemplo, marcar como anómalas las peores 10%
binary_predictions = (anomaly_scores < threshold).astype(int)

# Obtener las etiquetas reales de anomalías
real_labels = df['is_anomalous'].values

# Evaluar con métricas
accuracy = accuracy_score(real_labels, binary_predictions)
recall = recall_score(real_labels, binary_predictions)
precision = precision_score(real_labels, binary_predictions)
f1 = f1_score(real_labels, binary_predictions)

# Mostrar resultados
print(f"Accuracy: {accuracy:.2f}")
print(f"Recall: {recall:.2f}")
print(f"Precision: {precision:.2f}")
print(f"F1 Score: {f1:.2f}")
