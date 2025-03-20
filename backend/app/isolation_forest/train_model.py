import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Cargar los datos preprocesados
df = pd.read_csv("preprocessed_data1.csv")

# Eliminar columna 'is_anomalous' si está presente
if "is_anomalous" in df.columns:
    df = df.drop(columns=["is_anomalous"])

# Guardar los nombres de las columnas para más tarde
column_names = df.columns

# Normalizar los datos
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Volver a convertir X_scaled a DataFrame con los nombres de las columnas originales
X_scaled = pd.DataFrame(X_scaled, columns=column_names)

# Entrenar Isolation Forest con hiperparámetros optimizados
model = IsolationForest(n_estimators=200, contamination="auto", random_state=42, n_jobs=-1)
model.fit(X_scaled)

# Guardar el modelo entrenado y el scaler
joblib.dump(model, "isolation_forest2.pkl")
joblib.dump(scaler, "scaler2.pkl")

print("Modelo Isolation Forest guardado como 'isolation_forest.pkl'")
print("Scaler guardado como 'scaler.pkl'")
