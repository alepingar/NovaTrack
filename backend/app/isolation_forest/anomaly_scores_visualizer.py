import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
# Cargar datos con los scores de anomalía
df = pd.read_csv("anomaly_scores.csv")

# Configurar el gráfico
plt.figure(figsize=(10, 6))
sns.histplot(df["anomaly_score"], bins=50, kde=True)

# Etiquetas
plt.xlabel("Anomaly Score")
plt.ylabel("Número de Transacciones")
plt.title("Distribución de los Scores de Anomalía")

# Mostrar gráfico
plt.show()
