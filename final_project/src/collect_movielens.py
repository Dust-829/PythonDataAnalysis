from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import pandas as pd
import requests

from common import RAW_DIR, append_dictionary, ensure_project_dirs, now_iso, write_json


URLS = {
    "small": "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip",
    "full": "https://files.grouplens.org/datasets/movielens/ml-latest.zip",
}


def download_file(url: str, target: Path, force: bool = False) -> None:
    if target.exists() and target.stat().st_size > 0 and not force:
        print(f"Skip existing file: {target}")
        return
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)


def count_csv_rows(path: Path) -> int:
    try:
        return int(sum(1 for _ in path.open("rb")) - 1)
    except FileNotFoundError:
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and unpack MovieLens data.")
    parser.add_argument("--size", choices=URLS.keys(), default="small")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    ensure_project_dirs()
    url = URLS[args.size]
    zip_path = RAW_DIR / f"movielens-{args.size}.zip"
    extract_dir = RAW_DIR / f"movielens-{args.size}"

    download_file(url, zip_path, force=args.force)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_dir)

    csv_files = sorted(extract_dir.rglob("*.csv"))
    row_counts = {str(path.relative_to(RAW_DIR)): count_csv_rows(path) for path in csv_files}
    manifest = {
        "source": "MovieLens",
        "url": url,
        "dataset_size": args.size,
        "collected_at": now_iso(),
        "zip_file": str(zip_path.relative_to(RAW_DIR)),
        "zip_size_bytes": zip_path.stat().st_size,
        "row_counts": row_counts,
    }
    write_json(RAW_DIR / "movielens_manifest.json", manifest)

    append_dictionary(
        "MovieLens 数据源",
        [
            f"- 来源 URL：{url}",
            f"- 采集时间：{manifest['collected_at']}",
            f"- 数据规模：{args.size}",
            "- 主要文件：ratings.csv、movies.csv、links.csv、tags.csv。",
            "- 字段说明：userId 为用户编号，movieId 为电影编号，rating 为用户评分，timestamp 为评分时间戳，title 为电影标题，genres 为电影类型，imdbId/tmdbId 为外部平台 ID。",
            f"- 行数统计：{row_counts}",
        ],
    )
    print("MovieLens collection finished.")


if __name__ == "__main__":
    main()

