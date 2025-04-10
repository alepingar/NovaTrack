import pandas as pd
import numpy as np
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sklearn.preprocessing import MinMaxScaler
import joblib
from sklearn.metrics import recall_score, accuracy_score, precision_score, f1_score
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import ParameterGrid, train_test_split

class IsolationForestTuner:
    def __init__(self, data, features, is_anomalous_col):
        self.data = data
        self.features = features
        self.is_anomalous_col = is_anomalous_col

    def train_evaluate(self, params):
        """Entrena y evalúa el modelo con los parámetros dados."""
        X = self.data[self.features]
        y_true = self.data[self.is_anomalous_col]

        # Dividir los datos para una evaluación más robusta
        X_train, X_test, y_train, y_test = train_test_split(X, y_true, test_size=0.3, random_state=42, stratify=y_true)

        model = IsolationForest(random_state=42, n_jobs=-1, **params)
        model.fit(X_train)
        anomaly_scores_test = model.score_samples(X_test)

        # Definir un umbral (esto podría necesitar optimización también)
        threshold = np.percentile(anomaly_scores_test, 7.5)
        binary_predictions = (anomaly_scores_test < threshold).astype(int)

        accuracy = accuracy_score(y_test, binary_predictions)
        recall = recall_score(y_test, binary_predictions)
        precision = precision_score(y_test, binary_predictions)
        f1 = f1_score(y_test, binary_predictions)

        return {"accuracy": accuracy, "recall": recall, "precision": precision, "f1": f1}

    def find_best_params(self, param_grid, n_iter=10):
        """Busca los mejores parámetros utilizando una búsqueda aleatoria."""
        best_params = None
        best_f1 = -1
        results = []

        grid = list(ParameterGrid(param_grid))
        num_combinations = len(grid)

        print(f"Probando {min(n_iter, num_combinations)} de {num_combinations} combinaciones de parámetros...")

        # Si hay menos combinaciones que n_iter, probar todas
        if num_combinations < n_iter:
            param_combinations = grid
        else:
            param_combinations = np.random.choice(grid, n_iter, replace=False)

        for i, params in enumerate(param_combinations):
            print(f"\nEvaluando combinación {i+1}/{len(param_combinations)}: {params}")
            metrics = self.train_evaluate(params)
            results.append({"params": params, **metrics})
            print(f"Resultados: Accuracy={metrics['accuracy']:.2f}, Recall={metrics['recall']:.2f}, Precision={metrics['precision']:.2f}, F1={metrics['f1']:.2f}")

            if metrics["f1"] > best_f1:
                best_f1 = metrics["f1"]
                best_params = params

        print("\nMejor resultado encontrado:")
        print(f"Mejores parámetros: {best_params}")
        print(f"F1 Score: {best_f1:.2f}")

        return best_params

# --- Uso de la clase ---
async def main():
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
    df = await fetch_data()

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
    df = df.drop(columns=['status'])
    df = pd.concat([df, status_one_hot], axis=1)

    df['is_recurrent_client'] = 0
    recurrent_accounts = df['from_account'].value_counts()[df['from_account'].value_counts() > 1].index
    df.loc[df['from_account'].isin(recurrent_accounts), 'is_recurrent_client'] = 1
    df["hour"] = df["timestamp"].dt.hour

    features = ["amount_zscore", "is_recurrent_client", "hour", "is_outside_iqr"] + list(status_one_hot.columns)
    is_anomalous_col = 'is_anomalous' # Asegúrate de que esta columna exista en tu DataFrame

    tuner = IsolationForestTuner(df, features, is_anomalous_col)

    param_grid = {
        'n_estimators': [100, 200, 300, 400, 500],
        'max_samples': ['auto', 0.3, 0.5, 0.7, 0.9],
        'contamination': ['auto', 0.03, 0.05, 0.07, 0.1],
        'max_features': [0.3, 0.5, 0.7, 0.9, 1.0],
    }

    best_params = tuner.find_best_params(param_grid, n_iter=300) # Aumenté n_iter para una búsqueda más exhaustiva

    # Entrenar el modelo final con los mejores parámetros encontrados
    best_model = IsolationForest(random_state=42, n_jobs=-1, **best_params)
    X = df[features]
    best_model.fit(X)

    # Guardar el mejor modelo
    model_path = "best_isolation_forest.pkl"
    joblib.dump(best_model, model_path)
    print(f"\nMejor modelo guardado en: {model_path}")

if __name__ == "__main__":
    asyncio.run(main())