import shap
import pandas as pd
import numpy as np
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sklearn.preprocessing import MinMaxScaler
import joblib
import matplotlib.pyplot as plt

class ShapInsights:
    def __init__(self, model, data, features, shap_values=None):
        self.model = model
        self.data = data
        self.features = features
        self.shap_values = shap_values
    
    def calculate_shap_values(self):
        """
        Calcula los valores SHAP para el conjunto de datos dado.
        """
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(self.data[self.features])
        self.shap_values = shap_values
        return shap_values
    
    def plot_dependence(self, feature_name, interaction_feature=None, xmax=None):
        """
        Muestra el gráfico de dependencia de SHAP para una característica específica.
        
        Parameters:
        - feature_name: Nombre de la característica para la que se muestra el gráfico de dependencia.
        - interaction_feature: Característica con la que interactuar, si es necesario.
        - xmax: Limitar el valor máximo del eje X al percentil especificado.
        """
        if self.shap_values is None:
            self.calculate_shap_values()
        
        shap.dependence_plot(
            feature_name,
            self.shap_values,
            self.data[self.features],
            interaction_index=interaction_feature,
            xmax=xmax
        )
        plt.show()

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

# Cargar los valores SHAP para los 5000 primeros puntos de datos
shap_insights = ShapInsights(model, df, features)
shap_insights.calculate_shap_values()

# Visualizar el gráfico de dependencia para una característica
shap_insights.plot_dependence('amount_zscore')
shap_insights.plot_dependence('amount_zscore', interaction_feature='hour')

