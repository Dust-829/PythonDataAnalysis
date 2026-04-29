from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from common import FIGURES_DIR, METRICS_DIR, PROCESSED_DIR, TABLES_DIR, ensure_project_dirs, write_json


def main() -> None:
    ensure_project_dirs()
    path = PROCESSED_DIR / "movies_final.csv"
    if not path.exists():
        raise FileNotFoundError("Run src/clean_merge.py before clustering modeling.")

    movies = pd.read_csv(path, low_memory=False)
    feature_cols = [
        "movie_rating_count",
        "movie_rating_mean",
        "movie_rating_std",
        "release_year",
        "release_age",
        "runtimeMinutes",
        "averageRating",
        "numVotes",
        "tag_count",
        "tag_unique_count",
        "genre_count",
    ]
    feature_cols = [col for col in feature_cols if col in movies.columns]
    data = movies[feature_cols].copy()
    preprocess = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    X = preprocess.fit_transform(data)

    metrics = {}
    labels_map = {
        "kmeans": KMeans(n_clusters=4, random_state=42, n_init="auto").fit_predict(X),
        "agglomerative": AgglomerativeClustering(n_clusters=4).fit_predict(X),
    }
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    for name, labels in labels_map.items():
        movies[f"cluster_{name}"] = labels
        metrics[name] = {"silhouette": float(silhouette_score(X, labels))}
        plt.figure(figsize=(8, 5))
        sns.scatterplot(x=coords[:, 0], y=coords[:, 1], hue=labels, palette="tab10", s=35)
        plt.title(f"{name} Clustering Result")
        plt.xlabel("PCA 1")
        plt.ylabel("PCA 2")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / f"cluster_{name}.png", dpi=160)
        plt.close()
        summary = movies.groupby(f"cluster_{name}")[feature_cols].mean(numeric_only=True)
        summary.to_csv(TABLES_DIR / f"cluster_summary_{name}.csv", encoding="utf-8-sig")

    movies.to_csv(PROCESSED_DIR / "movies_with_clusters.csv", index=False, encoding="utf-8-sig")
    write_json(METRICS_DIR / "clustering_metrics.json", metrics)
    pd.DataFrame(metrics).T.to_csv(METRICS_DIR / "clustering_metrics.csv", encoding="utf-8-sig")
    print("Clustering models finished.")


if __name__ == "__main__":
    main()

