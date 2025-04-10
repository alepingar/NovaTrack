from sklearn.ensemble import IsolationForest
import pandas as pd
import joblib

# Cargar los datos preprocesados
df = pd.read_csv("preprocessed_data.csv")

# Guardar nombres de columnas
column_names = df.columns

# Entrenar Isolation Forest con n_estimators alto para mayor estabilidad
model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42, n_jobs=-1, max_features=1.0, max_samples="auto")
model.fit(df)

# Obtener los scores de anomalía
df["anomaly_score"] = model.score_samples(df)

# Guardar modelo y los scores
joblib.dump(model, "isolation_forest.pkl")
df.to_csv("anomaly_scores.csv", index=False)

print("Modelo entrenado y guardado con anomaly scores.")
