import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_full_download_preserves_repository_metadata(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    kaggle = fake_bin / "kaggle"
    kaggle.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
out=""
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "-p" ]]; then
    out="$2"
    shift 2
  else
    shift
  fi
done
mkdir -p "$out/cityrep_core/data/tasks/demo"
mkdir -p "$out/cityrep_core/splits/block10_5seed_mlp1024"
mkdir -p "$out/cityrep_core/splits/random_5seed_mlp1024"
mkdir -p "$out/cityrep_core/metadata/croissant"
mkdir -p "$out/cityrep_core/metadata"
mkdir -p "$out/embeddings/model/baselines/artifacts/model"
printf data > "$out/cityrep_core/data/tasks/demo/labels.tif"
printf spatial > "$out/cityrep_core/splits/block10_5seed_mlp1024/split.json"
printf random > "$out/cityrep_core/splits/random_5seed_mlp1024/split.json"
printf stale > "$out/cityrep_core/splits/manifest.csv"
printf stale > "$out/cityrep_core/metadata/croissant/cityrep.json"
printf stale > "$out/cityrep_core/metadata/model_directories.csv"
printf embedding > "$out/embeddings/model/baselines/artifacts/model/PACKAGE.json"
""",
        encoding="utf-8",
    )
    kaggle.chmod(0o755)

    destination = tmp_path / "release"
    metadata = destination / "metadata/croissant/cityrep.json"
    metadata.parent.mkdir(parents=True)
    metadata.write_text("current", encoding="utf-8")
    split_manifest = destination / "splits/manifest.csv"
    split_manifest.parent.mkdir(parents=True)
    split_manifest.write_text("current", encoding="utf-8")
    directory_manifest = destination / "metadata/model_directories.csv"
    directory_manifest.write_text("current", encoding="utf-8")

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["CITYREP_DOWNLOAD_ROOT"] = str(destination)
    subprocess.run(["bash", str(ROOT / "download.sh")], check=True, env=env)

    assert (destination / "data/tasks/demo/labels.tif").read_text() == "data"
    assert (destination / "splits/block10_5seed_mlp1024/split.json").read_text() == "spatial"
    assert (destination / "splits/random_5seed_mlp1024/split.json").read_text() == "random"
    assert (destination / "baselines/artifacts/model/PACKAGE.json").read_text() == "embedding"
    assert metadata.read_text() == "current"
    assert split_manifest.read_text() == "current"
    assert directory_manifest.read_text() == "current"
