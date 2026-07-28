#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".ipynb_checkpoints",
    "build",
    "dist",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write SHA256 checksums for release files.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=ROOT / "metadata" / "checksums" / "checksums.sha256")
    parser.add_argument("--include-data", action="store_true", help="Include data/tasks files in checksum output.")
    return parser.parse_args()


def skip(path: Path, root: Path, include_data: bool) -> bool:
    rel_parts = path.relative_to(root).parts
    if set(rel_parts).intersection(SKIP_DIRS):
        return True
    if any(part.endswith(".egg-info") for part in rel_parts):
        return True
    if path.name == ".DS_Store":
        return True
    if (
        not include_data
        and rel_parts[:2] == ("data", "tasks")
        and path.name != "README.md"
    ):
        return True
    if rel_parts[:2] == ("metadata", "checksums"):
        return True
    return False


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    rows = []
    for path in sorted(args.root.rglob("*")):
        if path.is_file() and not path.is_symlink() and not skip(path, args.root, args.include_data):
            rows.append(f"{sha256(path)}  {path.relative_to(args.root).as_posix()}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(args.out)
    print(f"files={len(rows)}")


if __name__ == "__main__":
    main()

