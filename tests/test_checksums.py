from pathlib import Path

from scripts.make_checksums import skip
from scripts.make_release_checksums import skip as skip_release


def test_checksum_skip_excludes_generated_cache_paths(tmp_path: Path) -> None:
    assert skip(tmp_path / ".pytest_cache" / "v" / "cache" / "nodeids", tmp_path, False)
    assert skip(tmp_path / "urban_benchmark.egg-info" / "PKG-INFO", tmp_path, False)
    assert skip(tmp_path / ".DS_Store", tmp_path, False)
    assert skip(tmp_path / "build" / "lib" / "urban_benchmark" / "cli.py", tmp_path, False)
    assert skip(tmp_path / "dist" / "urban_benchmark.whl", tmp_path, False)
    assert not skip(tmp_path / "README.md", tmp_path, False)
    assert not skip(tmp_path / "data" / "tasks.json", tmp_path, False)
    assert not skip(tmp_path / "data" / "registry" / "tasks.csv", tmp_path, False)
    assert not skip(tmp_path / "data" / "tasks" / "README.md", tmp_path, False)
    assert skip(tmp_path / "data" / "tasks" / "example" / "samples.parquet", tmp_path, False)
    assert not skip(tmp_path / "data" / "tasks" / "example" / "samples.parquet", tmp_path, True)


def test_release_checksum_skip_excludes_generated_cache_paths(tmp_path: Path) -> None:
    assert skip_release(tmp_path / ".pytest_cache" / "v" / "cache" / "nodeids", tmp_path)
    assert skip_release(tmp_path / "urban_benchmark.egg-info" / "PKG-INFO", tmp_path)
    assert skip_release(tmp_path / ".DS_Store", tmp_path)
    assert not skip_release(tmp_path / "metadata" / "embedding_manifest.csv", tmp_path)
