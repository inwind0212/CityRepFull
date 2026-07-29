from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin

from scripts.inspect_embedding_sample import inspect_sample, sha256


ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "metadata" / "sample_embedding.json"


def test_sample_metadata_matches_release_manifest() -> None:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    manifest = pd.read_csv(ROOT / "baselines" / "registry" / "embedding_manifest.csv")
    row = manifest.loc[
        manifest["model"].eq(metadata["model"])
        & manifest["task_id"].eq(metadata["task_id"])
    ].squeeze()

    assert bool(row["available"])
    assert row["artifact_path"] == metadata["source_artifact"]
    assert metadata["hosted_path"].startswith("cityrep_sample/")
    assert metadata["purpose"].endswith("not a benchmark evaluation subset.")
    assert len(metadata["sha256"]) == 64


def test_sample_inspector_accepts_matching_geotiff(tmp_path: Path) -> None:
    sample = tmp_path / "sample.tif"
    transform = from_origin(103.6, 1.48, 0.01, 0.01)
    with rasterio.open(
        sample,
        "w",
        driver="GTiff",
        width=4,
        height=3,
        count=2,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dataset:
        dataset.write(np.arange(24, dtype="float32").reshape(2, 3, 4))

    with rasterio.open(sample) as dataset:
        metadata = {
            "sample_id": "test-sample",
            "sha256": sha256(sample),
            "size_bytes": sample.stat().st_size,
            "width": dataset.width,
            "height": dataset.height,
            "embedding_dim": dataset.count,
            "dtype": dataset.dtypes[0],
            "crs": str(dataset.crs),
            "bounds": list(dataset.bounds),
        }
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    report = inspect_sample(sample, metadata_path)
    assert report["status"] == "ok"
    assert report["embedding_dim"] == 2


def test_sample_download_script_has_valid_shell_syntax() -> None:
    subprocess.run(
        ["bash", "-n", str(ROOT / "download_sample.sh")],
        check=True,
    )
