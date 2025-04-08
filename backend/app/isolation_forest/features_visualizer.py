import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

class FeatureVisualizer:
    def __init__(self, data_path="anomaly_scores.csv"):
        self.data_path = data_path
        self.df = None

    def load_data(self):
        """Carga los datos con los scores de anomalía."""
        self.df = pd.read_csv(self.data_path)
        print(f"Datos cargados con {self.df.shape[0]} filas y {self.df.shape[1]} columnas.")

    def plot_feature_scatter(self, feature_x="amount_zscore", feature_y="status"):
        """Grafica un scatter plot con dos features y el anomaly score como color."""
        if feature_x not in self.df.columns or feature_y not in self.df.columns:
            print("Error: Una de las características no existe en los datos.")
            return

        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(self.df[feature_x], self.df[feature_y], c=self.df["anomaly_score"], cmap="coolwarm", edgecolors="k")
        plt.colorbar(scatter, label="Anomaly Score")
        plt.xlabel(feature_x)
        plt.ylabel(feature_y)
        plt.title(f"Distribución de {feature_x} vs {feature_y} con Anomaly Score")
        plt.show()

# Uso de la clase
if __name__ == "__main__":
    visualizer = FeatureVisualizer()
    visualizer.load_data()
    visualizer.plot_anomaly_distribution()
    visualizer.plot_feature_scatter()
