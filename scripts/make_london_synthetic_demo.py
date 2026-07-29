#!/usr/bin/env python3
"""Generate the artificial London land-use schema example."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SAMPLES_PER_CLASS = 2
COORDINATE_DECIMALS = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--class-names",
        nargs=12,
        default=[f"class_{index}" for index in range(12)],
    )
    return parser.parse_args()


def synthetic_demo(class_names: list[str]) -> pd.DataFrame:
    if len(class_names) != 12:
        raise ValueError("Expected exactly 12 class names")
    rows = []
    for label_id, label in enumerate(class_names):
        for class_example in range(SAMPLES_PER_CLASS):
            index = label_id * SAMPLES_PER_CLASS + class_example
            rows.append(
                {
                    "sample_id": f"london_synthetic_{index:03d}",
                    "x": round(-0.50 + (index % 6) * 0.16, COORDINATE_DECIMALS),
                    "y": round(51.30 + (index // 6) * 0.14, COORDINATE_DECIMALS),
                    "label": str(label),
                    "label_id": label_id,
                    "block10_id": (index // 6) * 10 + (index % 6),
                    "release_scope": "synthetic_demo_only",
                    "is_synthetic": True,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    synthetic_demo(list(args.class_names)).to_parquet(
        args.out,
        index=False,
        compression="zstd",
    )
    print(args.out)


if __name__ == "__main__":
    main()
