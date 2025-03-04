import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Cargar los datos preprocesados
df = pd.read_csv("preprocessed_data.csv")

# Eliminar columna 'is_anomalous' si está presente
if "is_anomalous" in df.columns:
    df = df.drop(columns=["is_anomalous"])

# Normalizar los datos
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Entrenar Isolation Forest con hiperparámetros optimizados
model = IsolationForest(n_estimators=200, contamination=0.06, random_state=42, n_jobs=-1)
model.fit(X_scaled)

# Guardar el modelo entrenado y el scaler
joblib.dump(model, "isolation_forest.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Modelo Isolation Forest guardado como 'isolation_forest.pkl'")
print("Scaler guardado como 'scaler.pkl'")
