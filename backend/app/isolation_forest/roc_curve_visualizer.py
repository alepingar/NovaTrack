import pandas as pd
import numpy as np
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sklearn.preprocessing import MinMaxScaler
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

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
q1 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.15))
q3 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.85))
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
    
features = ["amount_zscore","is_recurrent_client","hour", "is_outside_iqr"] + list(status_one_hot.columns)
X = df[features]

# Hacer las predicciones (1: normal, -1: anómala)
predictions = model.predict(X)

# Convertir las predicciones a formato binario (1: normal, 0: anómala)
predictions = (predictions == -1).astype(int)

# Obtener las etiquetas reales de anomalías desde la base de datos (campo 'is_anomalous')
real_labels = df['is_anomalous'].values

# Calcular la Curva ROC del modelo Isolation Forest
fpr, tpr, _ = roc_curve(real_labels, predictions)
roc_auc = auc(fpr, tpr)

# Curva Naive (modelo aleatorio con distribución uniforme)
random_probs = np.random.uniform(0, 1, len(real_labels))
fpr_naive, tpr_naive, _ = roc_curve(real_labels, random_probs)
roc_auc_naive = auc(fpr_naive, tpr_naive)

# Configuración de la gráfica
plt.figure(figsize=(8,6))

# Curva del modelo
plt.plot(fpr, tpr, color='blue', lw=2, label=f'Isolation Forest (AUC = {roc_auc:.2f})')

# Curva Naive
plt.plot(fpr_naive, tpr_naive, 'r--', lw=2, label=f'Naive (AUC = {roc_auc_naive:.2f})')

# Curva Random
plt.plot([0, 1], [0, 1], color='gray', linestyle='--', lw=2, label='Random')

# Ajustar límites con margen
plt.xlim([-0.02, 1.02])
plt.ylim([-0.02, 1.02])

# Etiquetas y título
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Curva ROC - Isolation Forest')
plt.legend(loc='lower right')

# Mostrar la gráfica
plt.show()