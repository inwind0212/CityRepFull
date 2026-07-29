#!/usr/bin/env python3
"""Generate and verify the released task-level split files."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

import pandas as pd

from urban_benchmark.io import write_json
from urban_benchmark.protocols import load_protocol
from urban_benchmark.splits import load_fixed_splits, make_splits
from urban_benchmark.tasks import load_task, load_task_specs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-registry", default="data/tasks.json")
    parser.add_argument("--protocol-registry", default="configs/release/protocols.json")
    parser.add_argument(
        "--protocols",
        nargs="+",
        default=["block10_5seed_mlp1024", "random_5seed_mlp1024"],
    )
    parser.add_argument("--out-root", default="splits")
    return parser.parse_args()


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    args = parse_args()
    registry = Path(args.task_registry)
    task_specs = load_task_specs(registry)
    task_ids = sorted(
        task_id
        for task_id, spec in task_specs.items()
        if str(spec.get("availability", "full")) == "full"
    )
    manifest_rows: list[dict] = []

    for protocol_id in args.protocols:
        protocol = load_protocol(protocol_id, args.protocol_registry)
        split_cfg = dict(protocol["split"])
        split_cfg.pop("fixed_split_file", None)
        split_cfg.pop("fixed_split_root", None)
        suffix = str(split_cfg.pop("fixed_split_suffix", ".json"))
        protocol_root = Path(args.out_root) / protocol_id
        protocol_root.mkdir(parents=True, exist_ok=True)

        for task_id in task_ids:
            task = load_task(task_id, registry)
            folds = make_splits(task, split_cfg)
            payload = {
                "schema_version": "1.0",
                "task_id": task_id,
                "protocol_id": protocol_id,
                "sample_count": task.n_samples,
                "folds": [
                    {
                        "seed": split.seed,
                        "meta": split.meta,
                        "train": task.samples.iloc[split.train_idx]["sample_id"].astype(str).tolist(),
                        "val": task.samples.iloc[split.val_idx]["sample_id"].astype(str).tolist(),
                        "test": task.samples.iloc[split.test_idx]["sample_id"].astype(str).tolist(),
                    }
                    for split in folds
                ],
            }
            output = protocol_root / f"{task_id}{suffix}"
            if output.suffix == ".gz":
                with gzip.open(output, "wt", encoding="utf-8", compresslevel=9) as handle:
                    json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
            else:
                write_json(output, payload)
            load_fixed_splits(task, output, expected_seeds=split_cfg.get("seeds"))
            manifest_rows.append(
                {
                    "protocol_id": protocol_id,
                    "task_id": task_id,
                    "sample_count": task.n_samples,
                    "fold_count": len(folds),
                    "path": str(output.relative_to(Path(args.out_root).parent)),
                    "sha256": digest(output),
                }
            )

    manifest = Path(args.out_root) / "manifest.csv"
    pd.DataFrame(manifest_rows).to_csv(manifest, index=False)
    print(f"wrote {len(manifest_rows)} split files and {manifest}")


if __name__ == "__main__":
    main()
