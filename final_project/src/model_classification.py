from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from common import FIGURES_DIR, METRICS_DIR, PROCESSED_DIR, ensure_project_dirs, write_json


def main() -> None:
    ensure_project_dirs()
    path = PROCESSED_DIR / "ratings_final.csv"
    if not path.exists():
        raise FileNotFoundError("Run src/clean_merge.py before classification modeling.")

    df = pd.read_csv(path, low_memory=False).sample(frac=1, random_state=42)
    df = df.head(min(len(df), 80000))
    target = "is_high_rating"
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
    y = df[target].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    preprocess = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )
    models = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "decision_tree": DecisionTreeClassifier(max_depth=8, random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42, n_jobs=1),
        "knn": KNeighborsClassifier(n_neighbors=9),
    }
    metrics = {}
    plt.figure(figsize=(8, 6))
    for name, model in models.items():
        pipeline = Pipeline([("preprocess", preprocess), ("model", model)])
        pipeline.fit(X_train, y_train)
        pred = pipeline.predict(X_test)
        if hasattr(pipeline, "predict_proba"):
            score = pipeline.predict_proba(X_test)[:, 1]
        else:
            score = pred
        fpr, tpr, _ = roc_curve(y_test, score)
        model_auc = auc(fpr, tpr)
        metrics[name] = {
            "accuracy": float(accuracy_score(y_test, pred)),
            "precision": float(precision_score(y_test, pred, zero_division=0)),
            "recall": float(recall_score(y_test, pred, zero_division=0)),
            "f1": float(f1_score(y_test, pred, zero_division=0)),
            "auc": float(model_auc),
        }
        cm = confusion_matrix(y_test, pred)
        plt_cm = plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
        plt.title(f"Confusion Matrix - {name}")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.tight_layout()
        plt_cm.savefig(FIGURES_DIR / f"confusion_matrix_{name}.png", dpi=160)
        plt.close(plt_cm)
        plt.plot(fpr, tpr, label=f"{name} AUC={model_auc:.3f}")

    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Classification ROC Curves")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "classification_roc_curves.png", dpi=160)
    plt.close()

    write_json(METRICS_DIR / "classification_metrics.json", metrics)
    pd.DataFrame(metrics).T.to_csv(METRICS_DIR / "classification_metrics.csv", encoding="utf-8-sig")
    print("Classification models finished.")


if __name__ == "__main__":
    main()
