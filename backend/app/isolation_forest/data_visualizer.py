import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sklearn.preprocessing import MinMaxScaler

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

# Visualización de la distribución de datos
plt.style.use("ggplot")
fig, axes = plt.subplots(3, 1, figsize=(10, 12))

# Histograma de amount original
sns.histplot(df["amount"], bins=50, kde=True, ax=axes[0], color="blue")
axes[0].set_title("Distribución de Amount (Original)")
axes[0].set_xlabel("Amount")
axes[0].set_ylabel("Frecuencia")

# Histograma de amount después de log1p
sns.histplot(df["amount_zscore"], bins=50, kde=True, ax=axes[1], color="green")
axes[1].set_title("Distribución de Amount (Log1p Aplicado)")
axes[1].set_xlabel("log1p(Amount)")
axes[1].set_ylabel("Frecuencia")

plt.tight_layout()
plt.show()

# Boxplot para visualizar outliers
plt.figure(figsize=(8, 5))
sns.boxplot(x=df["amount"], color="blue")
plt.title("Boxplot de Amount (Original)")
plt.show()

# Convertir estado de la transferencia a valores numéricos
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
df["status"] = df["status"].map(status_mapping)

# Seleccionar columnas finales
features = ["amount_zscore", "status"]
X = df[features]

# Guardar los datos preprocesados en CSV para entrenar el modelo
X.to_csv("preprocessed_data.csv", index=False)
print("Datos preprocesados guardados en 'preprocessed_data.csv'")
