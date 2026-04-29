from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from common import (
    INTERIM_DIR,
    PROCESSED_DIR,
    RAW_DIR,
    append_dictionary,
    ensure_project_dirs,
    write_json,
)


def find_movielens_dir() -> Path:
    candidates = sorted(RAW_DIR.glob("movielens-*/*"))
    for path in candidates:
        if (path / "ratings.csv").exists() and (path / "movies.csv").exists():
            return path
    candidates = sorted(RAW_DIR.glob("movielens-*"))
    for path in candidates:
        if (path / "ratings.csv").exists() and (path / "movies.csv").exists():
            return path
    raise FileNotFoundError("MovieLens files not found. Run src/collect_movielens.py first.")


def read_imdb_file(filename: str, columns: list[str] | None = None) -> pd.DataFrame:
    path = RAW_DIR / "imdb" / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", compression="gzip", usecols=columns, na_values="\\N", low_memory=False)


def parse_title_year(title: pd.Series) -> pd.Series:
    return pd.to_numeric(title.str.extract(r"\((\d{4})\)\s*$")[0], errors="coerce")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and merge MovieLens and IMDb data.")
    parser.add_argument("--max-ratings", type=int, default=250000, help="Limit rows for local modeling speed.")
    args = parser.parse_args()

    ensure_project_dirs()
    ml_dir = find_movielens_dir()
    ratings = pd.read_csv(ml_dir / "ratings.csv")
    movies = pd.read_csv(ml_dir / "movies.csv")
    links = pd.read_csv(ml_dir / "links.csv")
    tags_path = ml_dir / "tags.csv"
    tags = pd.read_csv(tags_path) if tags_path.exists() else pd.DataFrame(columns=["movieId", "tag"])

    raw_counts = {
        "ratings_rows_raw": int(len(ratings)),
        "movies_rows_raw": int(len(movies)),
        "links_rows_raw": int(len(links)),
        "tags_rows_raw": int(len(tags)),
    }
    if len(ratings) > args.max_ratings:
        ratings = ratings.sample(args.max_ratings, random_state=42).sort_values(["userId", "timestamp"])

    duplicate_rows = int(ratings.duplicated(["userId", "movieId", "timestamp"]).sum())
    ratings = ratings.drop_duplicates(["userId", "movieId", "timestamp"]).copy()
    ratings["rating_datetime"] = pd.to_datetime(ratings["timestamp"], unit="s", errors="coerce")
    ratings["rating_year"] = ratings["rating_datetime"].dt.year
    ratings["rating_month"] = ratings["rating_datetime"].dt.month
    ratings["is_high_rating"] = (ratings["rating"] >= 4.0).astype(int)

    movies = movies.drop_duplicates("movieId").copy()
    movies["title_year"] = parse_title_year(movies["title"])
    movies["clean_title"] = movies["title"].str.replace(r"\s*\(\d{4}\)\s*$", "", regex=True)
    movies["genres"] = movies["genres"].replace("(no genres listed)", np.nan)
    movies["genre_count"] = movies["genres"].fillna("").str.split("|").apply(lambda values: len([v for v in values if v]))
    genre_dummies = movies["genres"].fillna("").str.get_dummies(sep="|").add_prefix("genre_")
    movies = pd.concat([movies, genre_dummies], axis=1)

    links = links.drop_duplicates("movieId").copy()
    links["tconst"] = "tt" + links["imdbId"].fillna(0).astype(int).astype(str).str.zfill(7)

    tag_summary = (
        tags.dropna(subset=["tag"])
        .assign(tag=lambda frame: frame["tag"].astype(str).str.lower().str.strip())
        .groupby("movieId")
        .agg(tag_count=("tag", "size"), tag_unique_count=("tag", "nunique"), tag_text=("tag", lambda x: " ".join(x.head(30))))
        .reset_index()
    )

    movie_stats = (
        ratings.groupby("movieId")
        .agg(
            movie_rating_count=("rating", "size"),
            movie_rating_mean=("rating", "mean"),
            movie_rating_std=("rating", "std"),
            movie_rating_median=("rating", "median"),
            movie_rating_min=("rating", "min"),
            movie_rating_max=("rating", "max"),
        )
        .reset_index()
    )
    user_stats = (
        ratings.groupby("userId")
        .agg(user_rating_count=("rating", "size"), user_rating_mean=("rating", "mean"))
        .reset_index()
    )

    basics = read_imdb_file(
        "title.basics.tsv.gz",
        ["tconst", "titleType", "primaryTitle", "originalTitle", "isAdult", "startYear", "runtimeMinutes", "genres"],
    )
    imdb_ratings = read_imdb_file("title.ratings.tsv.gz", ["tconst", "averageRating", "numVotes"])
    if not basics.empty:
        basics = basics[basics["titleType"].isin(["movie", "tvMovie"])].copy()
        basics["startYear"] = pd.to_numeric(basics["startYear"], errors="coerce")
        basics["runtimeMinutes"] = pd.to_numeric(basics["runtimeMinutes"], errors="coerce")
        basics = basics.rename(columns={"genres": "imdb_genres"})
    if not imdb_ratings.empty:
        imdb_ratings["averageRating"] = pd.to_numeric(imdb_ratings["averageRating"], errors="coerce")
        imdb_ratings["numVotes"] = pd.to_numeric(imdb_ratings["numVotes"], errors="coerce")

    movie_level = movies.merge(links, on="movieId", how="left").merge(tag_summary, on="movieId", how="left")
    movie_level = movie_level.merge(movie_stats, on="movieId", how="left")
    if not basics.empty:
        movie_level = movie_level.merge(basics, on="tconst", how="left")
    if not imdb_ratings.empty:
        movie_level = movie_level.merge(imdb_ratings, on="tconst", how="left")

    if "startYear" not in movie_level:
        movie_level["startYear"] = movie_level["title_year"]
    if "runtimeMinutes" not in movie_level:
        movie_level["runtimeMinutes"] = np.nan
    if "averageRating" not in movie_level:
        movie_level["averageRating"] = np.nan
    if "numVotes" not in movie_level:
        movie_level["numVotes"] = np.nan

    movie_level["release_year"] = movie_level["startYear"].fillna(movie_level["title_year"])
    movie_level["release_age"] = movie_level["release_year"].apply(lambda x: 2026 - x if pd.notna(x) else np.nan)
    movie_level["tag_count"] = movie_level["tag_count"].fillna(0).astype(int)
    movie_level["tag_unique_count"] = movie_level["tag_unique_count"].fillna(0).astype(int)
    movie_level["tag_text"] = movie_level["tag_text"].fillna("")
    runtime_median = movie_level["runtimeMinutes"].median()
    if pd.isna(runtime_median):
        runtime_median = 100
    movie_level["runtimeMinutes"] = movie_level["runtimeMinutes"].fillna(runtime_median)
    movie_level["averageRating"] = movie_level["averageRating"].fillna(movie_level["movie_rating_mean"])
    movie_level["numVotes"] = movie_level["numVotes"].fillna(movie_level["movie_rating_count"])

    final_ratings = ratings.merge(user_stats, on="userId", how="left").merge(movie_level, on="movieId", how="left")
    final_ratings["rating_gap_vs_movie_mean"] = final_ratings["rating"] - final_ratings["movie_rating_mean"]
    final_ratings["rating_gap_vs_user_mean"] = final_ratings["rating"] - final_ratings["user_rating_mean"]
    final_ratings["primary_genre"] = final_ratings["genres"].fillna("Unknown").str.split("|").str[0]

    missing_summary = final_ratings.isna().sum().sort_values(ascending=False)
    outlier_mask = ((final_ratings["rating"] < 0.5) | (final_ratings["rating"] > 5.0))
    cleaning_report = {
        **raw_counts,
        "ratings_rows_after_sampling": int(len(ratings) + duplicate_rows),
        "duplicate_rating_rows_removed": duplicate_rows,
        "rating_outlier_rows": int(outlier_mask.sum()),
        "final_rating_rows": int(len(final_ratings)),
        "final_rating_columns": int(final_ratings.shape[1]),
        "final_movie_rows": int(len(movie_level)),
        "final_movie_columns": int(movie_level.shape[1]),
        "top_missing_columns": missing_summary.head(20).astype(int).to_dict(),
    }

    movie_level.to_csv(PROCESSED_DIR / "movies_final.csv", index=False, encoding="utf-8-sig")
    final_ratings.to_csv(PROCESSED_DIR / "ratings_final.csv", index=False, encoding="utf-8-sig")
    missing_summary.to_csv(INTERIM_DIR / "missing_summary.csv", encoding="utf-8-sig")
    write_json(INTERIM_DIR / "cleaning_report.json", cleaning_report)

    append_dictionary(
        "最终处理数据字段",
        [
            "- `ratings_final.csv`：评分级最终数据，用于统计分析、回归、分类和展示。",
            "- `movies_final.csv`：电影级汇总数据，用于聚类和电影维度分析。",
            "- 关键字段包括：userId、movieId、rating、rating_datetime、rating_year、rating_month、title、genres、primary_genre、genre_count、release_year、release_age、movie_rating_mean、movie_rating_count、user_rating_mean、user_rating_count、averageRating、numVotes、tag_count、tag_unique_count、各 genre_* 编码字段等。",
            f"- 清洗报告：{cleaning_report}",
        ],
    )
    print(f"Cleaned rows: {len(final_ratings)}, columns: {final_ratings.shape[1]}")


if __name__ == "__main__":
    main()
