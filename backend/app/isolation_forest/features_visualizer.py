import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

# --- Clase de Visualización Mejorada (sin cambios respecto a la anterior) ---
class ModelAnalysisVisualizer:
    def __init__(self, dataframe_con_features_y_scores: pd.DataFrame):
        if not isinstance(dataframe_con_features_y_scores, pd.DataFrame):
            raise ValueError("Se esperaba un DataFrame de Pandas para inicializar ModelAnalysisVisualizer.")
        self.df = dataframe_con_features_y_scores.copy()
        print(f"ℹ️  ModelAnalysisVisualizer inicializado con datos de {self.df.shape[0]} filas y {self.df.shape[1]} columnas.")

    def plot_anomaly_score_histogram(self,
                                     columna_score: str,
                                     nombre_modelo: str = "Análisis Exploratorio"):
        if columna_score not in self.df.columns:
            print(f"❌ Error: La columna de scores '{columna_score}' no se encuentra en el DataFrame.")
            return

        plt.figure(figsize=(12, 7))
        sns.histplot(self.df[columna_score], bins=50, kde=True, color="darkcyan", edgecolor="black")
        plt.xlabel(f"Score de Anomalía ({columna_score.replace('_', ' ').title()})", fontsize=12)
        plt.ylabel("Frecuencia", fontsize=12)
        plt.title(f"Histograma de Scores de Anomalía ({nombre_modelo})", fontsize=16)
        plt.grid(True, linestyle='--', alpha=0.7)
        description = (
            "Este histograma muestra la distribución de los scores de anomalía del modelo.\n"
            "La forma de esta distribución puede ayudar a identificar umbrales y a entender\n"
            "la separación entre observaciones normales y anómalas."
        )
        plt.figtext(0.5, -0.12, description, ha="center", fontsize=10,
                    bbox={"facecolor":"ghostwhite", "edgecolor":"silver", "alpha":0.8, "pad":5})
        plt.subplots_adjust(bottom=0.28, top=0.92)
        plt.show()
        print(f"✅ Histograma para '{columna_score}' del {nombre_modelo} generado.")

    def plot_feature_scatter(self,
                             feature_x: str,
                             feature_y: str,
                             columna_score: str,
                             nombre_modelo: str = "Análisis Exploratorio"):
        required_columns = [feature_x, feature_y, columna_score]
        missing_cols = [col for col in required_columns if col not in self.df.columns]
        if missing_cols:
            print(f"❌ Error: Las siguientes columnas requeridas no existen en los datos: {', '.join(missing_cols)}")
            return

        sample_df = self.df
        max_points_for_scatter = 10000
        if len(self.df) > max_points_for_scatter:
            print(f"⚠️  Tomando una muestra de {max_points_for_scatter} puntos para el scatter plot (de {len(self.df)}).")
            sample_df = self.df.sample(n=max_points_for_scatter, random_state=42)

        plt.figure(figsize=(13, 8))
        scatter = plt.scatter(sample_df[feature_x], sample_df[feature_y],
                              c=sample_df[columna_score], cmap="coolwarm",
                              alpha=0.65, edgecolors="k", s=35)
        cbar = plt.colorbar(scatter)
        cbar.set_label(f"Score de Anomalía ({columna_score.replace('_', ' ').title()})", fontsize=12)
        cbar.ax.tick_params(labelsize=10)
        plt.xlabel(feature_x.replace('_', ' ').title(), fontsize=12)
        plt.ylabel(feature_y.replace('_', ' ').title(), fontsize=12)
        plt.title(f"Relación: {feature_x.replace('_', ' ').title()} vs {feature_y.replace('_', ' ').title()} (Color: Score Anomalía - {nombre_modelo})", fontsize=15)
        plt.grid(True, linestyle='--', alpha=0.6)
        description = (
            f"Visualización de '{feature_x.replace('_', ' ').title()}' vs '{feature_y.replace('_', ' ').title()}'.\n"
            f"El color indica el score de anomalía (rojo = más alto/anómalo, azul = más bajo/normal).\n"
            "Permite identificar si combinaciones específicas de features se asocian con scores elevados."
        )
        plt.figtext(0.5, -0.15, description, ha="center", fontsize=10,
                     bbox={"facecolor":"ghostwhite", "edgecolor":"silver", "alpha":0.8, "pad":5})
        plt.subplots_adjust(bottom=0.3, top=0.92)
        plt.show()
        print(f"✅ Scatter plot para '{feature_x}' vs '{feature_y}' del {nombre_modelo} generado.")

    def listar_features_numericas(self, excluir_columnas: list = None):
        if excluir_columnas is None:
            excluir_columnas = []
        try:
            numeric_cols = self.df.select_dtypes(include=np.number).columns.tolist()
            return [col for col in numeric_cols if col not in excluir_columnas]
        except Exception as e:
            print(f"❌ Error al listar features numéricas: {e}")
            return []

# --- Funciones de Carga y Preprocesamiento de Datos (sin cambios respecto a la anterior) ---
MONGO_URI_CONFIG = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME_CONFIG = "nova_track"
COLLECTION_NAME_CONFIG = "transfers"

async def fetch_data_from_mongo(uri, db_name, collection_name):
    """Obtiene datos de MongoDB."""
    print(f"⏳ Conectando a MongoDB ({uri}) y obteniendo datos de '{db_name}.{collection_name}'...")
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        db = client[db_name]
        transfers_collection = db[collection_name]
        cursor = transfers_collection.find({})
        data = await cursor.to_list(length=None)
        print(f"✅ Datos obtenidos de MongoDB: {len(data)} registros.")
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ Error al conectar/obtener datos de MongoDB: {e}")
        return pd.DataFrame()

def robust_datetime_conversion(series):
    """Convierte una serie a datetime UTC de forma robusta."""
    def convert_value(value):
        if pd.isna(value): return pd.NaT
        try:
            dt = pd.to_datetime(value)
        except Exception:
            try:
                dt = pd.to_datetime(value, errors='coerce')
            except Exception: return pd.NaT
        if pd.isna(dt): return pd.NaT
        if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
            return dt.tz_convert('UTC')
        else:
            try: return dt.tz_localize('UTC')
            except Exception: return dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')
    return series.apply(convert_value)

def preprocess_dataframe_for_analysis(df_raw: pd.DataFrame):
    """Aplica tu lógica de preprocesamiento al DataFrame."""
    print("⚙️  Iniciando preprocesamiento del DataFrame para análisis...")
    if df_raw.empty:
        print("❌ DataFrame de entrada vacío, no se puede preprocesar.")
        return pd.DataFrame(), pd.DataFrame() # Devolver dos DataFrames vacíos

    # Mantener el _id original para un posible merge futuro si es necesario
    df_raw_with_id = df_raw.copy()

    df = df_raw.copy()
    required_cols_initial = ['company_id', 'timestamp', 'amount', 'status', 'from_account']
    missing_initial = [col for col in required_cols_initial if col not in df.columns]
    if missing_initial:
        print(f"❌ Error Crítico: Faltan columnas esenciales en los datos crudos: {missing_initial}")
        return df_raw_with_id, pd.DataFrame()

    print("  - Convirtiendo 'timestamp' a datetime UTC...")
    if 'timestamp' in df.columns:
        df['timestamp'] = robust_datetime_conversion(df['timestamp'])
        if df['timestamp'].isnull().sum() > 0:
            print(f"    ⚠️ {df['timestamp'].isnull().sum()} timestamps no pudieron ser convertidos a datetime UTC.")
    else: print("    ⚠️ Columna 'timestamp' no encontrada. 'hour' no se podrá calcular correctamente.")

    # Guardar el índice original después de la conversión de timestamp pero antes de sample/sort
    # si _id no está presente o no es único, esto puede ser una forma de rastrear
    if '_id' not in df.columns: # Si no hay _id de mongo, usar el índice como fallback (menos robusto)
        df_raw_with_id = df.reset_index().rename(columns={'index': 'original_index'})
    else: # Si hay _id, asegurar que df_raw_with_id lo tiene para el merge
        df_raw_with_id = df_raw_with_id[['_id']].copy() # Solo necesitamos el _id
        df_raw_with_id = pd.concat([df_raw_with_id, df.drop(columns=['_id'], errors='ignore')], axis=1)


    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df = df.sort_values(by=["company_id", "timestamp"]).reset_index(drop=True) # ESTE ES EL ORDEN FINAL DE LAS FEATURES

    print("  - Calculando 'amount_zscore'...")
    if 'amount' in df.columns and 'company_id' in df.columns:
        df["amount_mean"] = df.groupby("company_id")["amount"].transform("mean")
        df["amount_std"] = df.groupby("company_id")["amount"].transform("std").fillna(0)
        df["amount_zscore"] = np.where(df["amount_std"] == 0, 0, (df["amount"] - df["amount_mean"]) / df["amount_std"].replace(0, 1e-9))
        df["amount_zscore"] = df["amount_zscore"].fillna(0).replace([np.inf, -np.inf], 0)
    else: df["amount_zscore"] = 0; print("    ⚠️ 'amount' o 'company_id' no encontradas. 'amount_zscore' será 0.")

    print("  - Calculando 'is_outside_iqr'...")
    if 'amount' in df.columns and 'company_id' in df.columns:
        q1 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.05))
        q3 = df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.95))
        df["is_outside_iqr"] = ((df["amount"] < q1) | (df["amount"] > q3)).astype(int)
        df["is_outside_iqr"] = df["is_outside_iqr"].fillna(0)
    else: df["is_outside_iqr"] = 0; print("    ⚠️ 'amount' o 'company_id' no encontradas. 'is_outside_iqr' será 0.")

    print("  - Aplicando One-Hot Encoding para 'status'...")
    status_cols_generated = []
    if 'status' in df.columns:
        try:
            status_one_hot = pd.get_dummies(df['status'], prefix='status', dummy_na=False, dtype=int)
            df = df.drop(columns=['status']) # Dropear solo si existe
            df = pd.concat([df, status_one_hot], axis=1)
            status_cols_generated = status_one_hot.columns.tolist()
        except Exception as e: print(f"    ❌ Error durante One-Hot Encoding de 'status': {e}")
    else: print("    ⚠️ Columna 'status' no encontrada.")

    print("  - Extrayendo 'hour'...")
    if 'timestamp' in df.columns and not df['timestamp'].isnull().all():
        df["hour"] = df["timestamp"].dt.hour
        if df["hour"].isnull().any():
            hour_median = df["hour"].median(); hour_median = 0 if pd.isna(hour_median) else int(hour_median)
            df["hour"] = df["hour"].fillna(hour_median)
        df["hour"] = df["hour"].astype(int)
    else: df["hour"] = 0; print("    ⚠️ 'timestamp' inválido o no encontrado. 'hour' será 0.")

    print("  - Calculando 'is_recurrent_client'...")
    if 'from_account' in df.columns and 'company_id' in df.columns:
        df['is_recurrent_client'] = df.groupby('company_id')['from_account'].transform(lambda x: x.duplicated(keep=False)).astype(int)
    else: df['is_recurrent_client'] = 0; print("    ⚠️ 'from_account' o 'company_id' no encontradas. 'is_recurrent_client' será 0.")

    features_modelo = ["amount_zscore", "is_recurrent_client", "hour", "is_outside_iqr"] + status_cols_generated
    X_final_list = []
    print(f"  - Construyendo DataFrame final de features: {features_modelo}")
    for feature_name in features_modelo:
        if feature_name in df.columns: X_final_list.append(df[feature_name])
        else: X_final_list.append(pd.Series(0, index=df.index, name=feature_name)); print(f"    ⚠️ Feature esperada '{feature_name}' no encontrada. Se creará como ceros.")
    if not X_final_list: return df_raw_with_id, pd.DataFrame()
    X_final = pd.concat(X_final_list, axis=1).fillna(0)

    print("✅ Preprocesamiento completado.")
    # Devolvemos df (que tiene el mismo orden y número de filas que X_final ahora)
    # y X_final. df_raw_with_id es para el merge de scores si es necesario.
    return df, X_final, df_raw_with_id


# --- Bloque Principal ---
if __name__ == "__main__":
    print("--- Iniciando Script de Análisis Adicional de Modelo (con Datos Reales y Scores de CSV) ---")

    # 1. Cargar Datos Reales de MongoDB
    try:
        raw_df = asyncio.run(fetch_data_from_mongo(MONGO_URI_CONFIG, DB_NAME_CONFIG, COLLECTION_NAME_CONFIG))
    except RuntimeError as e:
        if " asyncio.run() cannot be called from a running event loop" in str(e):
            loop = asyncio.get_event_loop(); raw_df = loop.run_until_complete(fetch_data_from_mongo(MONGO_URI_CONFIG, DB_NAME_CONFIG, COLLECTION_NAME_CONFIG))
        else: raise e

    if raw_df.empty:
        print("❌ No se cargaron datos de MongoDB o ocurrió un error. Terminando script.")
    else:
        # 2. Preprocesar los Datos
        # df_con_todas_cols_ordenado_como_X es el df que tiene las features y otras cols,
        # pero ya ha pasado por sample y sort, por lo que su orden coincide con X_modelo_features.
        # df_con_id_originales contiene las columnas originales (incluyendo _id si existe) ANTES del sample/sort,
        # pero alineado en filas con df_con_todas_cols_ordenado_como_X.
        df_despues_preproceso, X_modelo_features, df_para_merge_scores = preprocess_dataframe_for_analysis(raw_df)


        if X_modelo_features.empty:
            print("❌ El preprocesamiento no generó características. Terminando script.")
        else:
            print("\nPrimeras filas del DataFrame de features (X_modelo_features):")
            print(X_modelo_features.head())
            print(f"Forma de X_modelo_features: {X_modelo_features.shape}")

            # 3. CARGAR SCORES DE ANOMALÍA DESDE CSV
            path_scores_csv = "anomaly_scores.csv" # Asegúrate que este archivo exista
            nombre_columna_score_en_csv = "anomaly_score" # CAMBIA ESTO si tu columna se llama diferente
            df_para_visualizacion = X_modelo_features.copy() # Empezamos con las features
            
            print(f"\n🔄 Cargando scores de anomalía desde '{path_scores_csv}'...")
            if os.path.exists(path_scores_csv):
                try:
                    df_scores = pd.read_csv(path_scores_csv)
                    print(f"  ✅ Scores cargados de CSV. {len(df_scores)} scores encontrados.")

                    if nombre_columna_score_en_csv not in df_scores.columns:
                        print(f"  ❌ Error: La columna '{nombre_columna_score_en_csv}' no se encuentra en '{path_scores_csv}'.")
                        print(f"     Columnas disponibles en el CSV: {df_scores.columns.tolist()}")
                        print("     Continuando sin scores reales, se usarán scores simulados de emergencia.")
                        # Fallback a scores simulados si no se puede cargar la columna
                        df_para_visualizacion[nombre_columna_score_en_csv] = np.random.rand(len(X_modelo_features))

                    elif len(df_scores) != len(X_modelo_features):
                        print(f"  ⚠️ ADVERTENCIA: El número de scores en '{path_scores_csv}' ({len(df_scores)})")
                        print(f"     NO COINCIDE con el número de filas preprocesadas ({len(X_modelo_features)}).")
                        print("     Esto puede llevar a una asignación incorrecta de scores.")
                        print("     Asegúrate de que 'anomaly_scores.csv' corresponda EXACTAMENTE a los datos preprocesados.")
                        print("     Si el CSV tiene un ID, considera hacer un MERGE con 'df_para_merge_scores' usando '_id' o 'original_index'.")
                        # Opción 1: Truncar o rellenar (peligroso si el orden no es idéntico)
                        # Opción 2: Intentar un merge si df_scores tiene un ID y df_para_merge_scores también
                        # Por ahora, si las longitudes no coinciden, no se usarán los scores del CSV para evitar errores.
                        print("     Debido a la diferencia de longitud, se usarán scores simulados de emergencia.")
                        df_para_visualizacion[nombre_columna_score_en_csv] = np.random.rand(len(X_modelo_features))
                    else:
                        print("  ✅ Número de scores coincide con datos preprocesados. Asignando scores.")
                        # Asumimos que el orden es el correcto.
                        df_para_visualizacion[nombre_columna_score_en_csv] = df_scores[nombre_columna_score_en_csv].values
                        print(f"  Estadísticas descriptivas de los scores cargados ('{nombre_columna_score_en_csv}'):")
                        print(df_para_visualizacion[nombre_columna_score_en_csv].describe())

                except Exception as e:
                    print(f"  ❌ Error al cargar o procesar '{path_scores_csv}': {e}")
                    print("     Continuando sin scores reales, se usarán scores simulados de emergencia.")
                    df_para_visualizacion[nombre_columna_score_en_csv] = np.random.rand(len(X_modelo_features))
            else:
                print(f"  ❌ Error: El archivo '{path_scores_csv}' no fue encontrado.")
                print("     Continuando sin scores reales, se usarán scores simulados de emergencia.")
                df_para_visualizacion[nombre_columna_score_en_csv] = np.random.rand(len(X_modelo_features))


            # 4. Usar la Clase de Visualización
            visualizador = ModelAnalysisVisualizer(df_para_visualizacion)
            nombre_del_modelo_para_graficos = "Isolation Forest (Scores Reales)" # O el nombre de tu modelo

            # 4a. Generar Histograma de Scores
            print(f"\n📊 Generando Histograma de Scores ('{nombre_columna_score_en_csv}')...")
            visualizador.plot_anomaly_score_histogram(
                columna_score=nombre_columna_score_en_csv, # Usar el nombre de la columna cargada/simulada
                nombre_modelo=nombre_del_modelo_para_graficos
            )

            # 4b. Generar Scatter Plots de Features
            print("\n📈 Generando Scatter Plots de Características...")
            features_numericas_para_scatter = visualizador.listar_features_numericas(
                excluir_columnas=[nombre_columna_score_en_csv]
            )
            print(f"Características numéricas disponibles para scatter plots: {features_numericas_para_scatter}")

            pares_de_features_a_visualizar = []
            if 'amount_zscore' in features_numericas_para_scatter and 'hour' in features_numericas_para_scatter:
                pares_de_features_a_visualizar.append(('amount_zscore', 'hour'))
            status_cols_num = [col for col in features_numericas_para_scatter if col.startswith("status_")]
            if 'amount_zscore' in features_numericas_para_scatter and status_cols_num:
                 pares_de_features_a_visualizar.append(('amount_zscore', status_cols_num[0]))
            if not pares_de_features_a_visualizar and len(features_numericas_para_scatter) >= 2:
                pares_de_features_a_visualizar.append((features_numericas_para_scatter[0], features_numericas_para_scatter[1]))

            if pares_de_features_a_visualizar:
                for i, (f_x, f_y) in enumerate(pares_de_features_a_visualizar):
                    print(f"--- Generando Scatter Plot {i+1}/{len(pares_de_features_a_visualizar)}: {f_x} vs {f_y} ---")
                    visualizador.plot_feature_scatter(
                        feature_x=f_x,
                        feature_y=f_y,
                        columna_score=nombre_columna_score_en_csv,
                        nombre_modelo=nombre_del_modelo_para_graficos
                    )
            else:
                print("⚠️ No se pudieron seleccionar pares de features numéricas para los scatter plots.")

    print("\n🏁 Script de Análisis Adicional completado.")