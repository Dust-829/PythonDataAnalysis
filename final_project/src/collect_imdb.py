from __future__ import annotations

import argparse
from pathlib import Path

import requests

from common import RAW_DIR, append_dictionary, ensure_project_dirs, now_iso, write_json


BASE_URL = "https://datasets.imdbws.com"
DEFAULT_FILES = ["title.basics.tsv.gz", "title.ratings.tsv.gz", "title.crew.tsv.gz"]
OPTIONAL_FILES = ["name.basics.tsv.gz"]


def download_file(url: str, target: Path, force: bool = False) -> None:
    if target.exists() and target.stat().st_size > 0 and not force:
        print(f"Skip existing file: {target}")
        return
    with requests.get(url, stream=True, timeout=90) as response:
        response.raise_for_status()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download IMDb non-commercial datasets.")
    parser.add_argument("--include-names", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    ensure_project_dirs()
    imdb_dir = RAW_DIR / "imdb"
    files = DEFAULT_FILES + (OPTIONAL_FILES if args.include_names else [])
    manifest_files = {}
    collected_at = now_iso()

    for filename in files:
        url = f"{BASE_URL}/{filename}"
        target = imdb_dir / filename
        download_file(url, target, force=args.force)
        manifest_files[filename] = {
            "url": url,
            "size_bytes": target.stat().st_size if target.exists() else 0,
        }

    manifest = {
        "source": "IMDb Non-Commercial Datasets",
        "collected_at": collected_at,
        "files": manifest_files,
    }
    write_json(RAW_DIR / "imdb_manifest.json", manifest)

    append_dictionary(
        "IMDb 数据源",
        [
            f"- 来源 URL：{BASE_URL}/",
            f"- 采集时间：{collected_at}",
            "- 主要文件：title.basics.tsv.gz、title.ratings.tsv.gz、title.crew.tsv.gz。",
            "- 字段说明：tconst 为 IMDb 标题编号，titleType 为条目类型，primaryTitle/originalTitle 为标题，startYear 为上映年份，runtimeMinutes 为片长，genres 为类型，averageRating 为 IMDb 均分，numVotes 为投票数。",
            f"- 文件统计：{manifest_files}",
        ],
    )
    print("IMDb collection finished.")


if __name__ == "__main__":
    main()

