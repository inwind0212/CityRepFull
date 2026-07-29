from itertools import islice
from pathlib import Path

import mlcroissant as mlc

from urban_benchmark import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_release_version_is_consistent() -> None:
    assert __version__ == "1.0.0"


def test_croissant_metadata_validates_and_generates_records() -> None:
    dataset = mlc.Dataset(str(ROOT / "metadata" / "croissant" / "cityrep.json"))
    records = list(islice(dataset.records(record_set="release-components"), 6))
    assert len(records) == 6
    assert {row["release-components/component"] for row in records} == {
        "embedding-sample",
        "task-payloads",
        "spatial-splits",
        "random-splits",
        "model-embeddings",
        "embedding-index",
    }
