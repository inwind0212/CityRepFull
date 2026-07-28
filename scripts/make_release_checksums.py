#!/usr/bin/env python3
"""Create checksums for a CityRep Kaggle release directory."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd


SKIP_DIRS = {
    ".git",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}


def skip(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if set(rel_parts).intersection(SKIP_DIRS):
        return True
    if any(part.endswith(".egg-info") for part in rel_parts):
        return True
    return path.name == ".DS_Store"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", required=True, type=Path)
    parser.add_argument("--package-manifest", required=True, type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        help="Defaults to <release-root>/checksums/release.sha256.",
    )
    return parser.parse_args()


def sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    root = args.release_root.resolve()
    out = (args.out or root / "checksums" / "release.sha256").resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    packages = pd.read_csv(args.package_manifest)
    known_packages = {
        str(row.package_path): (int(row.size_bytes), str(row.sha256))
        for row in packages.itertuples(index=False)
    }
    if len(known_packages) != 11:
        raise ValueError(f"Expected 11 package records, found {len(known_packages)}")

    lines: list[str] = []
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.resolve() != out and not skip(path, root)
    )
    for path in files:
        relative = path.relative_to(root).as_posix()
        if relative in known_packages:
            expected_size, digest = known_packages[relative]
            if path.stat().st_size != expected_size:
                raise ValueError(
                    f"Package size mismatch for {relative}: "
                    f"{path.stat().st_size} != {expected_size}"
                )
        else:
            digest = sha256(path)
        lines.append(f"{digest}  {relative}")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[checksums] {len(lines)} files -> {out}")


if __name__ == "__main__":
    main()
