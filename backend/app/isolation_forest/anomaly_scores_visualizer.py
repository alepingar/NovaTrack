import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
# Cargar datos con los scores de anomalía
df = pd.read_csv("anomaly_scores.csv")

def generar_histograma_scores(dataframe: pd.DataFrame, 
                              columna_score: str = "anomaly_score", 
                              nombre_modelo: str = "Modelo"):
    """
    Genera y muestra un histograma de los scores de anomalía.

    Args:
        dataframe (pd.DataFrame): DataFrame que contiene la columna de scores.
        columna_score (str): Nombre de la columna que contiene los scores de anomalía.
        nombre_modelo (str): Nombre del modelo para incluir en el título.
    """
    if columna_score not in dataframe.columns:
        print(f"❌ Error: La columna de scores '{columna_score}' no se encuentra en el DataFrame.")
        return

    plt.figure(figsize=(12, 7))
    sns.histplot(dataframe[columna_score], bins=50, kde=True, color="teal", edgecolor="black")
    plt.xlabel(f"Score de Anomalía ({columna_score.replace('_', ' ').title()})", fontsize=12)
    plt.ylabel("Frecuencia (Número de Transacciones)", fontsize=12)
    plt.title(f"Distribución de Scores de Anomalía ({nombre_modelo})", fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    description = (
        "Este histograma muestra la distribución de los scores de anomalía asignados por el modelo.\n"
        "Valores más altos en el score suelen indicar una mayor probabilidad de que la transacción sea una anomalía.\n"
        "La forma de esta distribución ayuda a entender la separación entre datos normales y anómalos."
    )
    plt.figtext(0.5, -0.12, description, ha="center", fontsize=10,
                bbox={"facecolor":"lightyellow", "alpha":0.6, "pad":5})
    plt.subplots_adjust(bottom=0.25) # Ajustar para el figtext
    # Para guardar la figura, puedes añadir:
    # plt.savefig(f"histograma_scores_{nombre_modelo.replace(' ', '_')}.png", bbox_inches='tight')
    plt.show()
    print(f"✅ Histograma para '{columna_score}' del {nombre_modelo} generado.")


if __name__ == "__main__":

    generar_histograma_scores(df, "anomaly_score", "Modelo")
