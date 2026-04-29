from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from common import PROJECT_ROOT


EXCLUDED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    "tmp",
    "rendered",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
DEMO_PARTS = {"movielens-demo", "movielens-demo.zip", "demo_manifest.json"}


def should_include(path: Path, include_demo: bool) -> bool:
    rel = path.relative_to(PROJECT_ROOT)
    parts = set(rel.parts)
    if parts & EXCLUDED_PARTS:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if not include_demo and (parts & DEMO_PARTS):
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a clean submission zip.")
    parser.add_argument("--output", default="submission_project.zip")
    parser.add_argument("--include-demo", action="store_true", help="Include generated demo data. Do not use for final submission.")
    parser.add_argument("--allow-demo-outputs", action="store_true", help="Allow packaging when only demo data has been generated.")
    args = parser.parse_args()

    has_demo = (PROJECT_ROOT / "data" / "raw" / "demo_manifest.json").exists()
    has_real_movielens = (PROJECT_ROOT / "data" / "raw" / "movielens_manifest.json").exists()
    if has_demo and not has_real_movielens and not args.allow_demo_outputs:
        raise SystemExit(
            "Refuse to create final zip: current outputs appear to be based on demo data only. "
            "Run real data collection first, or pass --allow-demo-outputs for local testing."
        )

    output = PROJECT_ROOT / args.output
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in PROJECT_ROOT.rglob("*"):
            if path == output or path.is_dir() or not should_include(path, include_demo=args.include_demo):
                continue
            archive.write(path, path.relative_to(PROJECT_ROOT.parent))

    print(f"Submission zip generated: {output}")


if __name__ == "__main__":
    main()
