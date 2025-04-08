import pandas as pd
import numpy as np
import json
import os
import shap
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import recall_score, accuracy_score, precision_score, f1_score
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Cargar el modelo de Isolation Forest
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

# Convertir estado de la transferencia en valores numéricos
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
df["status"] = df["status"].map(status_mapping)

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

df["is_recurrent_client"] = 0
# Marcar todos los 'from_account' que aparecen más de una vez como recurrentes
recurrent_accounts = df['from_account'].value_counts()[df['from_account'].value_counts() > 1].index
df.loc[df['from_account'].isin(recurrent_accounts), 'is_recurrent_client'] = 1

features = ["amount_zscore", "is_outside_iqr", "status", "is_recurrent_client"]
X = df[features]

# SHAP: Crear explicaciones locales
explainer = shap.TreeExplainer(model)

# Elegir una muestra aleatoria de datos para explicar
random_indices = np.random.choice(len(X), 5000)
shap_values_random = explainer.shap_values(X.iloc[random_indices, :])
random_features = X.iloc[random_indices, :]

# Visualizar las explicaciones para el primer punto de la muestra aleatoria
shap.force_plot(explainer.expected_value, shap_values_random[0, :], random_features.iloc[0, :])

shap.summary_plot(shap_values_random, random_features)
