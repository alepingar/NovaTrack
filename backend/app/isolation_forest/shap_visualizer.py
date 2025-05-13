import pandas as pd
import numpy as np
import json
import os
import shap
import joblib
from sklearn.preprocessing import MinMaxScaler
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import matplotlib.pyplot as plt  # Importa matplotlib

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

# SHAP: Crear explicaciones locales
explainer = shap.TreeExplainer(model)

# Elegir una muestra aleatoria de datos para explicar
random_indices = np.random.choice(len(X), 1)  # Reducimos a una sola instancia para el force plot
shap_values_random = explainer.shap_values(X.iloc[random_indices, :])
random_features = X.iloc[random_indices, :]

# Generar el force plot
plt.figure()  # Crea una nueva figura
shap.force_plot(explainer.expected_value, shap_values_random[0, :], random_features.iloc[0, :], show=False, matplotlib=True)

# Guardar la figura como una imagen
output_path = "force_plot.png"
plt.savefig(output_path)
plt.close()  # Cierra la figura para liberar memoria

print(f"El force plot se ha guardado en: {output_path}")