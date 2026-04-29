from __future__ import annotations

import warnings

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

from common import FIGURES_DIR, PROCESSED_DIR, TABLES_DIR, ensure_project_dirs


warnings.filterwarnings("ignore", category=UserWarning)
sns.set_theme(style="whitegrid", font="SimHei")
plt.rcParams["axes.unicode_minus"] = False


def savefig(name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / name, dpi=160)
    plt.close()


def main() -> None:
    ensure_project_dirs()
    ratings_path = PROCESSED_DIR / "ratings_final.csv"
    if not ratings_path.exists():
        raise FileNotFoundError("Run src/clean_merge.py before EDA.")

    df = pd.read_csv(ratings_path, low_memory=False)
    sample = df.sample(min(len(df), 50000), random_state=42)
    numeric_cols = [
        "rating",
        "movie_rating_mean",
        "movie_rating_count",
        "user_rating_mean",
        "user_rating_count",
        "release_year",
        "release_age",
        "runtimeMinutes",
        "averageRating",
        "numVotes",
        "tag_count",
        "tag_unique_count",
    ]
    numeric_cols = [col for col in numeric_cols if col in df.columns]

    df[numeric_cols].describe(percentiles=[0.25, 0.5, 0.75, 0.9]).T.to_csv(
        TABLES_DIR / "descriptive_statistics.csv", encoding="utf-8-sig"
    )
    df["primary_genre"].value_counts().to_csv(TABLES_DIR / "genre_frequency.csv", encoding="utf-8-sig")
    pd.pivot_table(df, values="rating", index="primary_genre", columns="rating_year", aggfunc="mean").to_csv(
        TABLES_DIR / "pivot_genre_year_rating.csv", encoding="utf-8-sig"
    )
    df[numeric_cols].corr(method="spearman").to_csv(TABLES_DIR / "correlation_spearman.csv", encoding="utf-8-sig")

    plt.figure(figsize=(10, 4))
    sns.heatmap(sample.isna(), cbar=False)
    plt.title("Missing Value Distribution")
    savefig("missing_values_heatmap.png")

    yearly = df.groupby("rating_year")["rating"].mean().reset_index()
    plt.figure(figsize=(9, 5))
    sns.lineplot(data=yearly, x="rating_year", y="rating", marker="o")
    plt.title("Average Rating by Year")
    savefig("line_rating_year.png")

    top_genres = df["primary_genre"].value_counts().head(12)
    plt.figure(figsize=(9, 5))
    sns.barplot(x=top_genres.values, y=top_genres.index)
    plt.title("Top Genres by Rating Count")
    savefig("bar_top_genres.png")

    rating_counts = df["rating"].value_counts().sort_index()
    plt.figure(figsize=(6, 6))
    plt.pie(rating_counts.values, labels=rating_counts.index, autopct="%1.1f%%")
    plt.title("Rating Distribution")
    savefig("pie_rating_distribution.png")

    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=sample, x="release_year", y="rating", hue="primary_genre", legend=False, alpha=0.35)
    plt.title("Release Year vs User Rating")
    savefig("scatter_release_year_rating.png")

    top5 = df["primary_genre"].value_counts().head(5).index
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=sample[sample["primary_genre"].isin(top5)], x="primary_genre", y="rating")
    plt.title("Rating Outliers by Genre")
    savefig("boxplot_rating_by_genre.png")

    plt.figure(figsize=(8, 5))
    sns.histplot(df["movie_rating_mean"].dropna(), bins=30, kde=True)
    plt.title("Movie Average Rating Distribution")
    savefig("hist_movie_rating_mean.png")

    plt.figure(figsize=(9, 7))
    sns.heatmap(df[numeric_cols].corr(method="spearman"), cmap="coolwarm", center=0)
    plt.title("Spearman Correlation Heatmap")
    savefig("heatmap_correlation.png")

    plt.figure(figsize=(6, 6))
    stats.probplot(df["movie_rating_mean"].dropna(), dist="norm", plot=plt)
    plt.title("QQ Plot of Movie Average Rating")
    savefig("qq_movie_rating_mean.png")

    tag_text = " ".join(df.get("tag_text", pd.Series(dtype=str)).dropna().astype(str).head(20000))
    if tag_text.strip():
        try:
            from wordcloud import WordCloud

            wc = WordCloud(width=1200, height=600, background_color="white").generate(tag_text)
            plt.figure(figsize=(10, 5))
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            plt.title("Movie Tag Word Cloud")
            savefig("wordcloud_tags.png")
        except Exception:
            words = pd.Series(tag_text.split()).value_counts().head(20)
            plt.figure(figsize=(9, 5))
            sns.barplot(x=words.values, y=words.index)
            plt.title("Top Tag Words")
            savefig("wordcloud_tags_fallback.png")

    print("EDA tables and figures generated.")


if __name__ == "__main__":
    main()

