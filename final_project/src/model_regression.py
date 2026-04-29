from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common import FIGURES_DIR, METRICS_DIR, PROCESSED_DIR, ensure_project_dirs, write_json


def main() -> None:
    ensure_project_dirs()
    path = PROCESSED_DIR / "ratings_final.csv"
    if not path.exists():
        raise FileNotFoundError("Run src/clean_merge.py before regression modeling.")

    df = pd.read_csv(path, low_memory=False).sample(frac=1, random_state=42)
    df = df.head(min(len(df), 80000))
    target = "rating"
    numeric_features = [
        "movie_rating_count",
        "movie_rating_mean",
        "user_rating_count",
        "user_rating_mean",
        "release_year",
        "release_age",
        "runtimeMinutes",
        "averageRating",
        "numVotes",
        "tag_count",
        "tag_unique_count",
    ]
    numeric_features = [col for col in numeric_features if col in df.columns]
    categorical_features = ["primary_genre"]

    X = df[numeric_features + categorical_features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocess = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )
    models = {
        "linear_regression": LinearRegression(),
        "random_forest_regression": RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=1, max_depth=12),
    }
    metrics = {}
    predictions = {}
    for name, model in models.items():
        pipeline = Pipeline([("preprocess", preprocess), ("model", model)])
        pipeline.fit(X_train, y_train)
        pred = pipeline.predict(X_test)
        predictions[name] = pred
        metrics[name] = {
            "MAE": float(mean_absolute_error(y_test, pred)),
            "MSE": float(mean_squared_error(y_test, pred)),
            "R2": float(r2_score(y_test, pred)),
        }

    write_json(METRICS_DIR / "regression_metrics.json", metrics)
    pd.DataFrame(metrics).T.to_csv(METRICS_DIR / "regression_metrics.csv", encoding="utf-8-sig")

    plt.figure(figsize=(8, 5))
    for name, pred in predictions.items():
        plt.scatter(y_test, pred, alpha=0.18, s=10, label=name)
    plt.xlabel("Actual Rating")
    plt.ylabel("Predicted Rating")
    plt.title("Regression Predictions")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "regression_predictions.png", dpi=160)
    plt.close()
    print("Regression models finished.")


if __name__ == "__main__":
    main()
