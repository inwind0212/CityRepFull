#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import rasterio


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "sample" / "singapore_alphaearth_pm25_mean__6b89dbc081.tif"
DEFAULT_METADATA = ROOT / "metadata" / "sample_embedding.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and summarize the representative CityRep embedding sample."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_sample(path: Path, metadata_path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Sample file not found: {path}")
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Sample metadata not found: {metadata_path}")

    expected = json.loads(metadata_path.read_text(encoding="utf-8"))
    actual_hash = sha256(path)
    if actual_hash != expected["sha256"]:
        raise ValueError(
            f"SHA256 mismatch for {path}: expected {expected['sha256']}, got {actual_hash}"
        )

    with rasterio.open(path) as dataset:
        actual = {
            "size_bytes": path.stat().st_size,
            "width": dataset.width,
            "height": dataset.height,
            "embedding_dim": dataset.count,
            "dtype": dataset.dtypes[0],
            "crs": str(dataset.crs),
            "bounds": list(dataset.bounds),
        }

    for key in ("size_bytes", "width", "height", "embedding_dim", "dtype", "crs"):
        if actual[key] != expected[key]:
            raise ValueError(
                f"Metadata mismatch for {key}: expected {expected[key]!r}, "
                f"got {actual[key]!r}"
            )

    if any(abs(float(a) - float(b)) > 1e-9 for a, b in zip(actual["bounds"], expected["bounds"])):
        raise ValueError(
            f"Metadata mismatch for bounds: expected {expected['bounds']!r}, "
            f"got {actual['bounds']!r}"
        )

    return {
        "status": "ok",
        "sample_id": expected["sample_id"],
        "sha256": actual_hash,
        **actual,
    }


def main() -> None:
    args = parse_args()
    report = inspect_sample(args.input, args.metadata)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
