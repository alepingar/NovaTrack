import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

class TransferDataProcessorVisualizer:
    """
    A class to fetch, preprocess, and visualize transfer data from MongoDB.
    Includes advanced feature engineering and visualization techniques.
    """
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="nova_track", collection_name="transfers"):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.df = None

    async def _fetch_data(self):
        """Fetches data from MongoDB."""
        client = AsyncIOMotorClient(self.mongo_uri)
        db = client[self.db_name]
        collection = db[self.collection_name]
        cursor = collection.find({})
        data = await cursor.to_list(length=None)
        return pd.DataFrame(data)

    async def load_data(self):
        """Loads data into the DataFrame."""
        self.df = await self._fetch_data()
        return self.df

    def preprocess_data(self):
        """Preprocesses the transfer data, including feature engineering."""
        if self.df is None:
            raise ValueError("Data must be loaded first. Call load_data().")

        self.df = self.df.sample(frac=1).reset_index(drop=True)
        self.df = self.df.sort_values(by=["company_id", "timestamp"])

        # Calcular estadísticas por empresa
        self.df["amount_mean"] = self.df.groupby("company_id")["amount"].transform("mean")
        self.df["amount_std"] = self.df.groupby("company_id")["amount"].transform("std")
        self.df["amount_zscore"] = (self.df["amount"] - self.df["amount_mean"]) / self.df["amount_std"]

        # Calcular percentiles para detección de outliers por empresa
        q_low = self.df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.05))
        q_high = self.df.groupby("company_id")["amount"].transform(lambda x: x.quantile(0.95))
        self.df["amount_lower_bound"] = q_low
        self.df["amount_upper_bound"] = q_high
        self.df["is_outlier"] = ((self.df["amount"] < self.df["amount_lower_bound"]) | (self.df["amount"] > self.df["amount_upper_bound"])).astype(int)

        # One-Hot Encoding para la columna 'status'
        status_one_hot = pd.get_dummies(self.df['status'], prefix='status')
        self.df = self.df.drop(columns=['status'])
        self.df = pd.concat([self.df, status_one_hot], axis=1)

        # Convert boolean columns to integer (0 or 1)
        for col in status_one_hot.columns:
            self.df[col] = self.df[col].astype(int)

        # Feature de la hora de la transferencia
        self.df["hour"] = self.df["timestamp"].dt.hour

        # Feature de cliente recurrente
        self.df['is_recurrent_client'] = 0
        recurrent_accounts = self.df['from_account'].value_counts()[self.df['from_account'].value_counts() > 1].index
        self.df.loc[self.df['from_account'].isin(recurrent_accounts), 'is_recurrent_client'] = 1

        print("Data preprocessing complete.")
        print(self.df.isnull().sum())
        return self.df

    def visualize_distributions(self):
        """Visualizes the distribution of the 'amount' feature before and after transformation."""
        if self.df is None:
            raise ValueError("Data must be loaded first. Call load_data().")

        plt.style.use("ggplot")
        fig, axes = plt.subplots(3, 1, figsize=(10, 15))

        # Histograma de amount original
        sns.histplot(self.df["amount"], bins=50, kde=True, ax=axes[0], color="blue")
        axes[0].set_title("Distribución de Amount (Original)")
        axes[0].set_xlabel("Amount")
        axes[0].set_ylabel("Frecuencia")

        # Histograma de amount después de z-score
        sns.histplot(self.df["amount_zscore"], bins=50, kde=True, ax=axes[1], color="green")
        axes[1].set_title("Distribución de Amount (Z-score Normalizado)")
        axes[1].set_xlabel("Z-score(Amount)")
        axes[1].set_ylabel("Frecuencia")

        # Boxplot para visualizar outliers
        sns.boxplot(x=self.df["amount"], color="blue", ax=axes[2])
        axes[2].set_title("Boxplot de Amount (Original)")
        axes[2].set_xlabel("Amount")

        plt.tight_layout()
        plt.show()

    def visualize_outliers(self):
        """Visualizes outliers using boxplots, grouped by company if possible."""
        if self.df is None:
            raise ValueError("Data must be loaded first. Call load_data().")

        plt.figure(figsize=(12, 6))
        if 'company_id' in self.df.columns:
            sns.boxplot(x='company_id', y='amount', data=self.df)
            plt.title('Boxplot de Amount por Empresa (Detección de Outliers)')
            plt.xlabel('Company ID')
            plt.ylabel('Amount')
        else:
            sns.boxplot(x=self.df["amount"], color="blue")
            plt.title("Boxplot de Amount (Detección de Outliers)")
            plt.xlabel("Amount")
        plt.show()

    def visualize_feature_correlations(self, features_to_correlate=None):
        """Visualizes the correlation matrix of selected features."""
        if self.df is None:
            raise ValueError("Data must be loaded first. Call load_data().")

        if features_to_correlate is None:
            # Select numerical features for correlation analysis
            numerical_df = self.df.select_dtypes(include=np.number)
            corr_matrix = numerical_df.corr()
        else:
            corr_matrix = self.df[features_to_correlate].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title("Matriz de Correlación de Características")
        plt.show()

    def visualize_dimensionality_reduction(self, method='pca', n_components=2, features=None):
        """
        Applies dimensionality reduction (PCA or t-SNE) and visualizes the results.

        Args:
            method (str): 'pca' for Principal Component Analysis or 'tsne' for t-Distributed Stochastic Neighbor Embedding.
            n_components (int): Number of components to reduce to (for visualization, usually 2 or 3).
            features (list, optional): List of feature names to use for dimensionality reduction.
                                       If None, uses all numerical features.
        """
        if self.df is None:
            raise ValueError("Data must be loaded first. Call load_data().")

        numerical_df = self.df.select_dtypes(include=np.number).dropna()
        if features:
            X = numerical_df[features]
        else:
            X = numerical_df

        if X.shape[1] <= n_components:
            print(f"Number of features ({X.shape[1]}) is not greater than the number of components ({n_components}). Skipping dimensionality reduction.")
            return

        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        if method == 'pca':
            pca = PCA(n_components=n_components)
            X_reduced = pca.fit_transform(X_scaled)
            explained_variance_ratio = pca.explained_variance_ratio_
            print(f"Explained variance ratio for {n_components} components: {explained_variance_ratio}")
            if n_components == 2:
                plt.figure(figsize=(10, 8))
                sns.scatterplot(x=X_reduced[:, 0], y=X_reduced[:, 1])
                plt.xlabel('Principal Component 1')
                plt.ylabel('Principal Component 2')
                plt.title('Visualización PCA de los Datos')
                plt.show()
            elif n_components == 3:
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, projection='3d')
                ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2])
                ax.set_xlabel('Principal Component 1')
                ax.set_ylabel('Principal Component 2')
                ax.set_zlabel('Principal Component 3')
                plt.title('Visualización PCA 3D de los Datos')
                plt.show()

        elif method == 'tsne':
            if X_scaled.shape[0] < 30:
                print("Not enough samples for t-SNE. Skipping.")
                return
            tsne = TSNE(n_components=n_components, random_state=42, perplexity=min(30, X_scaled.shape[0] - 1))
            X_reduced = tsne.fit_transform(X_scaled)
            if n_components == 2:
                plt.figure(figsize=(10, 8))
                sns.scatterplot(x=X_reduced[:, 0], y=X_reduced[:, 1])
                plt.xlabel('t-SNE Dimension 1')
                plt.ylabel('t-SNE Dimension 2')
                plt.title('Visualización t-SNE de los Datos')
                plt.show()
            elif n_components == 3:
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, projection='3d')
                ax.scatter(X_reduced[:, 0], X_reduced[:, 1], X_reduced[:, 2])
                ax.set_xlabel('t-SNE Dimension 1')
                ax.set_ylabel('t-SNE Dimension 2')
                ax.set_zlabel('t-SNE Dimension 3')
                plt.title('Visualización t-SNE 3D de los Datos')
                plt.show()
        else:
            raise ValueError(f"Method '{method}' not supported. Choose 'pca' or 'tsne'.")

    def save_preprocessed_data(self, filename="preprocessed_data.csv", features_to_save=None):
        """Saves the preprocessed data to a CSV file."""
        if self.df is None:
            raise ValueError("Data must be loaded and preprocessed first.")

        if features_to_save:
            self.df[features_to_save].to_csv(filename, index=False)
            print(f"Preprocessed data (selected features) saved to '{filename}'")
        else:
            self.df.to_csv(filename, index=False)
            print(f"Preprocessed data saved to '{filename}'")

async def main():
    processor = TransferDataProcessorVisualizer()
    await processor.load_data()
    processor.preprocess_data()
    processor.visualize_distributions()
    processor.visualize_outliers()
    processor.visualize_feature_correlations(features_to_correlate=["amount", "amount_zscore", "hour", "is_recurrent_client", "is_outlier"] + [col for col in processor.df.columns if col.startswith('status_')])
    processor.visualize_dimensionality_reduction(method='pca', n_components=2, features=["amount_zscore", "hour", "is_recurrent_client", "is_outlier"] + [col for col in processor.df.columns if col.startswith('status_')])
    processor.visualize_dimensionality_reduction(method='tsne', n_components=2, features=["amount_zscore", "hour", "is_recurrent_client", "is_outlier"] + [col for col in processor.df.columns if col.startswith('status_')])
    processor.save_preprocessed_data(features_to_save=["amount_zscore", "is_recurrent_client", "hour", "is_outlier"] + [col for col in processor.df.columns if col.startswith('status_')])

if __name__ == "__main__":
    asyncio.run(main())