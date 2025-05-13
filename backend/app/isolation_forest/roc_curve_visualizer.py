import pandas as pd
import numpy as np
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from datetime import datetime, timezone # Asegurar import

# --- Configuración ---
MODEL_PATH = "isolation_forest.pkl" # Asegúrate que esta es la ruta correcta
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "nova_track"
COLLECTION_NAME = "transfers"
# --------------------

# --- Cargar Modelo ---
model_feature_names = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print(f"✅ Modelo cargado correctamente desde: {MODEL_PATH}")
    if hasattr(model, 'feature_names_in_'):
        model_feature_names = model.feature_names_in_
        print(f"ℹ️  El modelo fue entrenado con las siguientes características (orden incluido): {model_feature_names.tolist()}")
    else:
        print("⚠️ Advertencia: El modelo no tiene 'feature_names_in_'. Se intentará inferir el orden de características, lo cual puede ser propenso a errores si no coincide exactamente con el entrenamiento.")
else:
    print(f"❌ Error: El modelo no se encuentra en la ruta: {MODEL_PATH}")
    exit()

# --- Conexión a MongoDB ---
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
transfers_collection = db[COLLECTION_NAME]

# --- Obtener Datos ---
async def fetch_data():
    print("⏳ Obteniendo datos de MongoDB...")
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)
    if not data:
        print("❌ Error: No se encontraron datos en la colección.")
        return pd.DataFrame()
    print(f"✅ Datos obtenidos: {len(data)} registros.")
    return pd.DataFrame(data)

df = asyncio.run(fetch_data())

if df.empty:
    exit()

# --- Feature Engineering (Alineado con el script de preprocesamiento original) ---

# 1. Procesamiento de Timestamps
print("⚙️  Procesando Timestamps...")
if 'timestamp' not in df.columns:
    print("❌ Error: La columna 'timestamp' no existe en los datos.")
    exit()

original_timestamps_count = len(df)

def parse_and_convert_to_utc(value):
    if pd.isna(value):
        return pd.NaT
    try:
        # Intentar parsear el valor. Si ya es datetime, pd.to_datetime lo deja como está.
        # Si es un string, intenta convertirlo.
        dt_obj = pd.to_datetime(value)

        # Ahora manejar la zona horaria
        if dt_obj.tzinfo is not None and dt_obj.tzinfo.utcoffset(dt_obj) is not None: # Es tz-aware
            return dt_obj.tz_convert('UTC')
        else: # Es tz-naive o tzinfo es None pero utcoffset es None
            return dt_obj.tz_localize('UTC') # Asumir UTC para naive
    except Exception as e_parse:
        # Si pd.to_datetime(value) falla para un valor individual (e.g. string malformado)
        # o si tz_localize falla (ej. sobre un datetime ya aware después de un parseo parcial)
        # Devolver NaT para este valor problemático
        # print(f"Debug: No se pudo procesar el timestamp '{value}'. Error: {e_parse}") # Descomentar para depurar valores específicos
        return pd.NaT

# Aplicar la función a cada elemento de la columna 'timestamp'
df['timestamp_utc'] = df['timestamp'].apply(parse_and_convert_to_utc)

nulos_timestamp = df['timestamp_utc'].isnull().sum()
if nulos_timestamp > 0:
    print(f"⚠️ Advertencia: {nulos_timestamp} de {original_timestamps_count} timestamps no pudieron ser convertidos directamente a datetime UTC y son NaT.")
    if nulos_timestamp == original_timestamps_count:
        print("❌ Error Crítico: Todos los timestamps son inválidos o no pudieron ser procesados. Verifica el formato de 'timestamp' en MongoDB.")
        # Considerar salir si 'hour' es crucial y todos los timestamps son NaT
        # exit()

df['timestamp'] = df['timestamp_utc']
df.drop(columns=['timestamp_utc'], inplace=True, errors='ignore')


df = df.sort_values(by=["company_id", "timestamp"]).reset_index(drop=True)

print("  - Extrayendo 'hour'...")
df["hour"] = df["timestamp"].dt.hour # .dt.hour dará NaN si el timestamp es NaT
if df["hour"].isnull().any():
    nan_hour_count = df['hour'].isnull().sum()
    print(f"⚠️ Rellenando {nan_hour_count} valores nulos en 'hour' con 0 (debido a NaT en timestamp).")
    df["hour"] = df["hour"].fillna(0)
df["hour"] = df["hour"].astype(int)

print("⚙️  Aplicando ingeniería de características...")
df["amount_mean"] = df.groupby("company_id")["amount"].transform("mean")
df["amount_std"] = df.groupby("company_id")["amount"].transform("std")
df["amount_std"] = df["amount_std"].fillna(0)
df.loc[df["amount_std"] == 0, "amount_std"] = 1

df["amount_zscore"] = (df["amount"] - df["amount_mean"]) / df["amount_std"]
df["amount_zscore"] = df["amount_zscore"].fillna(0)

q1 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.05))
q3 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.95))
df["amount_iqr_low"] = q1
df["amount_iqr_high"] = q3
df["is_outside_iqr"] = ((df["amount"] < df["amount_iqr_low"]) | (df["amount"] > df["amount_iqr_high"])).astype(int)
df["is_outside_iqr"] = df["is_outside_iqr"].fillna(0)

status_one_hot_columns = []
print("  - Aplicando One-Hot Encoding para 'status'...")
if 'status' in df.columns:
    status_one_hot = pd.get_dummies(df['status'], prefix='status', dummy_na=False)
    df = df.drop(columns=['status'])
    df = pd.concat([df, status_one_hot.astype(int)], axis=1)
    status_one_hot_columns = status_one_hot.columns.tolist()
    print(f"  - Columnas de status generadas por get_dummies: {status_one_hot_columns}")
else:
    print("⚠️ Advertencia: La columna 'status' no se encontró en los datos. No se crearán columnas OHE para 'status'.")

print("  - Calculando 'is_recurrent_client'...")
if 'from_account' in df.columns:
    df['is_recurrent_client'] = df.groupby('company_id')['from_account'] \
                                 .transform(lambda x: x.duplicated(keep=False)).astype(int)
else:
    print("⚠️ Advertencia: La columna 'from_account' no se encontró. 'is_recurrent_client' no se calculará (o se establecerá a 0 si es esperada).")
    if model_feature_names and "is_recurrent_client" in model_feature_names:
        df['is_recurrent_client'] = 0


print("✅ Ingeniería de características completada.")

# --- Preparar Datos para el Modelo ---
if model_feature_names is not None:
    features_to_use = model_feature_names.tolist()
    print(f"ℹ️  Utilizando el orden de características del modelo entrenado: {features_to_use}")
else:
    base_features = ["amount_zscore", "is_recurrent_client", "hour", "is_outside_iqr"]
    features_to_use = base_features + status_one_hot_columns
    print(f"⚠️ El modelo no tiene 'feature_names_in_'. Usando el orden de características inferido: {features_to_use}")
    print("   Esto puede causar errores si no coincide exactamente con el entrenamiento.")

current_columns = df.columns.tolist()
for feature_col in features_to_use:
    if feature_col not in current_columns:
        print(f"⚠️ La característica esperada por el modelo '{feature_col}' no se generó/encontró en el DataFrame actual. Se añadirá como una columna de ceros.")
        df[feature_col] = 0

try:
    X = df[features_to_use]
except KeyError as e:
    missing_cols = [col for col in features_to_use if col not in df.columns]
    print(f"❌ Error Crítico: Faltan columnas indispensables para crear X, incluso después de intentar añadir las faltantes: {missing_cols}")
    print(f"   Columnas disponibles en df: {df.columns.tolist()}")
    print(f"   Columnas esperadas por el modelo (features_to_use): {features_to_use}")
    exit()

if X.isnull().values.any():
    print("⚠️ Advertencia: Se encontraron valores NaN en las características X finales. Rellenando con 0...")
    X = X.fillna(0)

print(f"ℹ️  Forma final de X antes de la predicción: {X.shape}")
print(f"ℹ️  Columnas finales de X: {X.columns.tolist()}")

# --- Cálculo ROC/AUC ---
print("📊 Calculando curva ROC y AUC...")
if 'is_anomalous' not in df.columns:
    print("⚠️ Advertencia: La columna 'is_anomalous' (etiqueta real) no se encuentra en los datos.")
    print("    Para calcular ROC/AUC, se necesita esta columna con valores 0 (normal) o 1 (anómalo).")
    print("    Añadiendo una columna 'is_anomalous' de ejemplo con todos ceros (normal) para que el script continúe, pero el AUC no será significativo.")
    df['is_anomalous'] = 0

real_labels = df['is_anomalous'].astype(int)
anomaly_scores = np.array([])
fpr, tpr, roc_auc = np.array([0, 1]), np.array([0, 1]), 0.0 # Valores por defecto

if X.empty:
    print("❌ Error: El DataFrame de características X está vacío. No se puede calcular ROC/AUC.")
else:
    try:
        anomaly_scores = -model.score_samples(X)
    except Exception as e:
        print(f"❌ Error al ejecutar model.score_samples(X): {e}")
        print(f"   Verificar la forma y contenido de X. Forma de X: {X.shape}")
        if not X.empty:
            print(f"   NaNs en X: {X.isnull().sum().sum()}")
            print(f"   Infs en X: {np.isinf(X).sum().sum()}")
        plt.text(0.5, 0.5, 'Error en score_samples', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')

    if anomaly_scores.size > 0 and len(np.unique(real_labels)) >= 2 :
        try:
            fpr, tpr, thresholds = roc_curve(real_labels, anomaly_scores)
            roc_auc = auc(fpr, tpr)
            print(f"✅ AUC Calculado: {roc_auc:.4f}")
        except ValueError as e:
            print(f"❌ Error durante el cálculo de roc_curve o auc: {e}")
            fpr, tpr, roc_auc = np.array([0,1]), np.array([0,1]), 0.0
            plt.text(0.5, 0.5, 'Error al calcular ROC/AUC', horizontalalignment='center', verticalalignment='center', fontsize=12, color='red')
    elif anomaly_scores.size == 0 and not X.empty: # Si X no estaba vacío pero no hay scores
        print("⚠️ No se generaron anomaly_scores (X podría tener problemas). No se puede calcular ROC/AUC.")
    elif not X.empty: # len(np.unique(real_labels)) < 2
        print(f"⚠️ Advertencia: Solo se encontró una clase ({np.unique(real_labels)}) en 'real_labels' o no hay suficientes datos.")
        roc_auc = 0.5
        print(f"⚠️ AUC establecido a {roc_auc} debido a una sola clase o datos insuficientes.")

# --- Generar Gráfica ROC ---
print("📈 Generando gráfica ROC...")
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label=f'Isolation Forest (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--', lw=2, label='Aleatorio (AUC = 0.50)')
plt.xlim([-0.02, 1.02])
plt.ylim([-0.02, 1.02])
plt.xlabel('Tasa de Falsos Positivos (FPR)')
plt.ylabel('Tasa de Verdaderos Positivos (TPR / Recall)')
plt.title('Curva ROC - Modelo Isolation Forest')
plt.legend(loc='lower right')
plt.grid(True)
plt.show()

print("🏁 Proceso completado.")