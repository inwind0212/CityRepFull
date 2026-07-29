from pathlib import Path

import pandas as pd

from urban_benchmark.cli import _directory_tree_stats


ROOT = Path(__file__).resolve().parents[1]


def test_model_directory_manifest_matches_public_layout() -> None:
    manifest = pd.read_csv(ROOT / "metadata" / "model_directories.csv")
    assert len(manifest) == 11
    assert manifest["model"].nunique() == 11
    assert manifest["distribution_path"].str.startswith("embeddings/").all()
    assert manifest["install_prefix"].str.startswith("baselines/artifacts/").all()
    contains_zip = manifest.astype(str).apply(
        lambda column: column.str.contains(".zip", regex=False)
    )
    assert not contains_zip.any().any()
    assert int(manifest["file_count"].sum()) == 509
    assert (manifest["total_size_bytes"] > 0).all()
    assert manifest["tree_sha256"].str.fullmatch(r"[0-9a-f]{64}").all()


def test_directory_tree_digest_is_path_aware(tmp_path: Path) -> None:
    nested = tmp_path / "city"
    nested.mkdir()
    artifact = nested / "embedding.bin"
    artifact.write_bytes(b"embedding")

    original = _directory_tree_stats(tmp_path)
    artifact.rename(nested / "renamed.bin")
    renamed = _directory_tree_stats(tmp_path)

    assert original[:2] == (1, 9)
    assert renamed[:2] == (1, 9)
    assert original[2] != renamed[2]
