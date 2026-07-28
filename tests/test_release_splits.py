from __future__ import annotations

import gzip
import json

import geopandas as gpd
import numpy as np
import pytest

from urban_benchmark.splits import load_fixed_splits
from urban_benchmark.tasks import Task


def make_task() -> Task:
    ids = [f"s{i}" for i in range(6)]
    samples = gpd.GeoDataFrame(
        {"sample_id": ids, "x": np.arange(6), "y": np.arange(6)},
        geometry=gpd.points_from_xy(np.arange(6), np.arange(6)),
        crs="EPSG:4326",
    )
    return Task("test.regression.2026", "regression", samples, np.zeros((6, 1)), ["label"])


def write_split(path, payload) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle)


def test_load_fixed_split_by_sample_id(tmp_path):
    task = make_task()
    path = tmp_path / "split.json.gz"
    write_split(
        path,
        {
            "folds": [
                {
                    "seed": 42,
                    "meta": {"method": "spatial_block"},
                    "train": ["s3", "s0", "s5"],
                    "val": ["s2"],
                    "test": ["s4", "s1"],
                }
            ]
        },
    )
    split = load_fixed_splits(task, path, expected_seeds=[42])[0]
    assert split.train_idx.tolist() == [3, 0, 5]
    assert split.val_idx.tolist() == [2]
    assert split.test_idx.tolist() == [4, 1]


def test_fixed_split_rejects_overlap(tmp_path):
    task = make_task()
    path = tmp_path / "bad.json.gz"
    write_split(
        path,
        {
            "folds": [
                {
                    "seed": 42,
                    "train": ["s0", "s1", "s2"],
                    "val": ["s2", "s3"],
                    "test": ["s4", "s5"],
                }
            ]
        },
    )
    with pytest.raises(ValueError, match="overlapping"):
        load_fixed_splits(task, path, expected_seeds=[42])
