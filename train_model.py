import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Cargar los datos preprocesados
df = pd.read_csv("preprocessed_data.csv")

# Entrenar Isolation Forest
model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
model.fit(df)

# Guardar el modelo entrenado
joblib.dump(model, "isolation_forest.pkl")
print("Modelo Isolation Forest guardado como 'isolation_forest.pkl'")
