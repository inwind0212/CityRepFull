from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
LONDON_TASK = "london.landuse.2026"


def test_public_release_scope_is_internally_consistent() -> None:
    tasks = json.loads((ROOT / "data" / "tasks.json").read_text())["tasks"]
    availability = {
        task_id: str(spec.get("availability", "full"))
        for task_id, spec in tasks.items()
    }
    assert len(tasks) == 64
    synthetic_demo_count = list(availability.values()).count("synthetic_demo_only")
    assert synthetic_demo_count == 1
    assert list(availability.values()).count("full") == len(tasks) - synthetic_demo_count

    london = tasks[LONDON_TASK]
    assert london["availability"] == "synthetic_demo_only"
    assert london["release_n_samples"] == 24
    assert london["benchmark_reproduction"] is False
    assert london["synthetic"] is True
    assert "full_benchmark_n_samples" not in london

    manifest = pd.read_csv(ROOT / "baselines" / "registry" / "embedding_manifest.csv")
    available = manifest["available"].astype(str).str.lower().isin({"true", "1", "yes"})
    london_rows = manifest[manifest["task_id"].eq(LONDON_TASK)]
    assert len(manifest) == 704
    assert int(available.sum()) == 693
    assert len(london_rows) == 11
    assert not london_rows["available"].astype(str).str.lower().isin({"true", "1", "yes"}).any()
    assert set(london_rows["release_scope"]) == {"synthetic_demo_only_no_embedding"}

    splits = pd.read_csv(ROOT / "splits" / "manifest.csv")
    assert len(splits) == 126
    released_task_count = len(tasks) - synthetic_demo_count
    assert splits["protocol_id"].value_counts().to_dict() == {
        "block10_5seed_mlp1024": released_task_count,
        "random_5seed_mlp1024": released_task_count,
    }
    assert not splits["task_id"].eq(LONDON_TASK).any()


def test_synthetic_london_generator_uses_only_fixed_artificial_rows() -> None:
    path = ROOT / "scripts" / "make_london_synthetic_demo.py"
    spec = importlib.util.spec_from_file_location("make_london_synthetic_demo", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    classes = [f"class_{index}" for index in range(12)]
    first = module.synthetic_demo(classes)
    second = module.synthetic_demo(classes)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 24
    assert first["sample_id"].is_unique
    assert first["sample_id"].str.fullmatch(r"london_synthetic_\d{3}").all()
    assert first.groupby("label").size().eq(2).all()
    assert first["is_synthetic"].eq(True).all()
    assert first["release_scope"].eq("synthetic_demo_only").all()


def test_model_registry_publishes_embeddings_only() -> None:
    registry = json.loads((ROOT / "baselines" / "registry" / "models.json").read_text())
    assert len(registry["models"]) == 11
    for model in registry["models"]:
        assert model["embedding_rows"] == 64
        assert model["synthetic_demo_rows"] == 1
        assert model["release_asset"] == "frozen_embeddings_only"
        assert "available_rows" not in model
        assert "code_path" not in model
    assert not (ROOT / "baselines" / "code").exists()
