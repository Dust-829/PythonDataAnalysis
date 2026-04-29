from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from common import RAW_DIR, append_dictionary, ensure_project_dirs, now_iso, write_json


GENRES = ["Action", "Comedy", "Drama", "Romance", "Sci-Fi", "Thriller", "Crime", "Animation", "Adventure", "Documentary"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate demo MovieLens-like data for offline smoke tests.")
    parser.add_argument("--ratings", type=int, default=30000)
    parser.add_argument("--movies", type=int, default=1200)
    parser.add_argument("--users", type=int, default=900)
    args = parser.parse_args()

    ensure_project_dirs()
    rng = np.random.default_rng(42)
    base_dir = RAW_DIR / "movielens-demo" / "ml-latest-small"
    base_dir.mkdir(parents=True, exist_ok=True)

    movie_ids = np.arange(1, args.movies + 1)
    titles = [f"Demo Movie {i} ({rng.integers(1980, 2025)})" for i in movie_ids]
    movie_genres = ["|".join(rng.choice(GENRES, size=rng.integers(1, 4), replace=False)) for _ in movie_ids]
    movies = pd.DataFrame({"movieId": movie_ids, "title": titles, "genres": movie_genres})

    ratings = pd.DataFrame(
        {
            "userId": rng.integers(1, args.users + 1, size=args.ratings),
            "movieId": rng.choice(movie_ids, size=args.ratings),
            "rating": rng.choice(np.arange(0.5, 5.5, 0.5), size=args.ratings, p=[0.03, 0.04, 0.06, 0.09, 0.12, 0.16, 0.18, 0.16, 0.11, 0.05]),
            "timestamp": rng.integers(1262304000, 1767139200, size=args.ratings),
        }
    )
    links = pd.DataFrame({"movieId": movie_ids, "imdbId": movie_ids + 1000000, "tmdbId": movie_ids + 2000000})
    tags = pd.DataFrame(
        {
            "userId": rng.integers(1, args.users + 1, size=args.movies * 2),
            "movieId": rng.choice(movie_ids, size=args.movies * 2),
            "tag": rng.choice(["classic", "funny", "slow", "visual", "family", "dark", "popular", "emotional"], size=args.movies * 2),
            "timestamp": rng.integers(1262304000, 1767139200, size=args.movies * 2),
        }
    )

    movies.to_csv(base_dir / "movies.csv", index=False)
    ratings.to_csv(base_dir / "ratings.csv", index=False)
    links.to_csv(base_dir / "links.csv", index=False)
    tags.to_csv(base_dir / "tags.csv", index=False)

    zip_path = RAW_DIR / "movielens-demo.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in base_dir.glob("*.csv"):
            archive.write(path, path.relative_to(RAW_DIR / "movielens-demo"))

    manifest = {
        "source": "Generated demo data for offline smoke tests only",
        "collected_at": now_iso(),
        "ratings": args.ratings,
        "movies": args.movies,
        "users": args.users,
        "warning": "Do not use this demo data for final course submission.",
    }
    write_json(RAW_DIR / "demo_manifest.json", manifest)
    append_dictionary(
        "Demo 数据说明",
        [
            "- 本数据仅用于无网络环境下验证代码流程，不用于最终课程提交。",
            f"- 生成时间：{manifest['collected_at']}",
            f"- 评分记录数：{args.ratings}",
            f"- 电影数量：{args.movies}",
            f"- 用户数量：{args.users}",
        ],
    )
    print("Demo data generated for smoke tests only.")


if __name__ == "__main__":
    main()

