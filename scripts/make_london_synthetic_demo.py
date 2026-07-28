#!/usr/bin/env python3
"""Replace the restricted London land-use payload with a synthetic demo.

The public 24-row payload contains two artificial examples for every CityRep
land-use class. Coordinates and labels are generated from fixed constants; no
Verisk coordinate, label, identifier, attribute, or geometry is retained. The
non-redistributed reference task remains documented because it produced the
reported paper results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd


TASK_ID = "london.landuse.2026"
FULL_N_SAMPLES = 100_000
SAMPLES_PER_CLASS = 2
COORDINATE_DECIMALS = 3
EULA_URL = "https://digimap.edina.ac.uk/help/copyright-and-licensing/verisk_eula/"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/"
SOURCE = "CityRep synthetic schema demonstration; no third-party land-use records"
LICENSE = "CC BY 4.0"
ATTRIBUTION = "CityRep maintainers"
RELEASE_NOTE = "Synthetic schema example; see task metadata."

PACKAGE_MEMBERS_TO_REMOVE = {
    "sphere2vec_fixed": [
        "baselines/artifacts/sphere2vec_fixed/london/"
        "london.landuse.2026_sphere2vec_spherec_fixed_f64.parquet",
    ],
    "space2vec": [
        "baselines/artifacts/space2vec/london/"
        "london_Space2Vec_fsq_second_locenc_landuse_points_d128__f6a77997f4.parquet",
    ],
    "calliper": [
        "baselines/artifacts/calliper/london/"
        "london_CaLLiPer_landuse_points_d128__339c7c2a5b.parquet",
    ],
    "satclip": [
        "baselines/artifacts/satclip/london/"
        "london_SatCLIP_ViT16_L40_landuse_points_d256__8ab7b42989.parquet",
    ],
    "alphaearth": [
        "baselines/artifacts/alphaearth/london/"
        "london.landuse.2026_alphaearth_sample_aligned.parquet",
        "baselines/artifacts/alphaearth/london/"
        "london.landuse.2026_alphaearth_sample_aligned.alignment.json",
    ],
    "aether": [
        "baselines/artifacts/aether/london/"
        "london.landuse.2026_aether_sample_aligned.parquet",
        "baselines/artifacts/aether/london/"
        "london.landuse.2026_aether_sample_aligned.alignment.json",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--code-root", type=Path)
    parser.add_argument("--strip-embedding-archives", action="store_true")
    return parser.parse_args()


def sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def synthetic_demo(class_names: list[str]) -> pd.DataFrame:
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


def update_task_payload(root: Path) -> int:
    task_dir = root / "data" / "tasks" / TASK_ID
    samples_path = task_dir / "samples.parquet"
    metadata_path = task_dir / "task.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    extract = synthetic_demo([str(value) for value in metadata["class_names"]])
    extract.to_parquet(samples_path, index=False, compression="zstd")

    metadata.update(
        {
            "source": SOURCE,
            "license": LICENSE,
            "license_url": CC_BY_URL,
            "attribution": ATTRIBUTION,
            "release_status": "synthetic_demo_only",
            "benchmark_reproduction": False,
            "full_data_redistributed": False,
            "synthetic": True,
            "n_samples": int(len(extract)),
            "reference_benchmark_n_samples": FULL_N_SAMPLES,
            "reference_task_source": (
                "Verisk UKLand data accessed through EDINA Digimap; "
                "used only for the reported reference results"
            ),
            "reference_task_license_url": EULA_URL,
            "reference_task_attribution": (
                "Digital Map Data © The GeoInformation Group Limited 2026"
            ),
            "class_counts": {
                str(label): int(count)
                for label, count in extract["label"].value_counts().sort_index().items()
            },
            "release_note": RELEASE_NOTE,
            "processing": [
                "The public payload is generated from fixed artificial coordinates and the released CityRep class-name list.",
                "Two synthetic rows are created for every class.",
                "No coordinate, label, sample identifier, source attribute, or geometry is copied or derived from Verisk.",
                "No public benchmark split or sample-aligned embedding is released for this task.",
            ],
        }
    )
    metadata.pop("source_path", None)
    metadata.pop("full_benchmark_n_samples", None)
    metadata.pop("full_benchmark_class_counts", None)
    metadata["generation_script"] = "scripts/make_london_synthetic_demo.py"
    metadata["sampling_meta"] = {
        "city": "london",
        "task": "landuse",
        "task_type": "classification",
        "sampling": "deterministic_synthetic_grid",
        "samples_per_class": SAMPLES_PER_CLASS,
        "samples": int(len(extract)),
        "coordinate_rounding_decimals": COORDINATE_DECIMALS,
        "benchmark_evaluation_supported": False,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return int(len(extract))


def update_task_registries(root: Path, n_extract: int) -> None:
    tasks_path = root / "data" / "tasks.json"
    registry = json.loads(tasks_path.read_text(encoding="utf-8"))
    spec = registry["tasks"][TASK_ID]
    spec.update(
        {
            "source": SOURCE,
            "license": LICENSE,
            "license_url": CC_BY_URL,
            "attribution": ATTRIBUTION,
            "availability": "synthetic_demo_only",
            "release_n_samples": n_extract,
            "reference_benchmark_n_samples": FULL_N_SAMPLES,
            "synthetic": True,
            "reference_task_source": "Verisk UKLand via EDINA Digimap; reference results only",
            "reference_task_license_url": EULA_URL,
            "benchmark_reproduction": False,
            "release_note": RELEASE_NOTE,
        }
    )
    spec.pop("full_benchmark_n_samples", None)
    tasks_path.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    csv_path = root / "data" / "registry" / "tasks.csv"
    tasks = pd.read_csv(csv_path)
    tasks["availability"] = tasks.get("availability", "full")
    tasks["availability"] = tasks["availability"].fillna("full")
    tasks["release_note"] = tasks.get("release_note", "")
    mask = tasks["task_id"].eq(TASK_ID)
    tasks.loc[mask, "source"] = SOURCE
    tasks.loc[mask, "license"] = LICENSE
    tasks.loc[mask, "availability"] = "synthetic_demo_only"
    tasks.loc[mask, "release_note"] = RELEASE_NOTE
    tasks.to_csv(csv_path, index=False)


def update_splits(root: Path) -> None:
    manifest_path = root / "splits" / "manifest.csv"
    manifest = pd.read_csv(manifest_path)
    london_rows = manifest[manifest["task_id"].eq(TASK_ID)]
    if len(london_rows) not in {0, 2}:
        raise ValueError(f"Expected zero or two London split rows, found {len(london_rows)}")
    for row in london_rows.itertuples(index=False):
        path = root / str(row.path)
        if path.is_file():
            path.unlink()
    manifest = manifest[~manifest["task_id"].eq(TASK_ID)].copy()
    manifest.to_csv(manifest_path, index=False)


def update_embedding_manifest(root: Path) -> None:
    path = root / "metadata" / "embedding_manifest.csv"
    manifest = pd.read_csv(path)
    manifest["release_scope"] = manifest.get("release_scope", "full")
    manifest["release_scope"] = manifest["release_scope"].fillna("full")
    mask = manifest["task_id"].eq(TASK_ID)
    if int(mask.sum()) != 11:
        raise ValueError(f"Expected 11 London embedding rows, found {int(mask.sum())}")
    manifest.loc[mask, "available"] = False
    manifest.loc[mask, "path_exists"] = False
    manifest.loc[mask, "release_scope"] = "synthetic_demo_only_no_embedding"
    manifest.loc[mask, "alignment_policy"] = (
        "Not released for public evaluation: the London payload is a synthetic "
        "schema demo and has no corresponding benchmark embeddings."
    )
    manifest.to_csv(path, index=False)


def update_landuse_caveats(root: Path) -> None:
    path = root / "metadata" / "landuse_license_caveats.csv"
    caveats = pd.read_csv(path)
    mask = caveats["task_id"].eq(TASK_ID)
    caveats.loc[mask, "status"] = "synthetic_demo_only"
    caveats.loc[mask, "note"] = (
        "The released 24-row London payload is fully synthetic and CC BY 4.0; "
        "it contains no Verisk-derived coordinates or labels. Reported reference "
        "results used a non-redistributed Verisk UKLand task. "
        f"Reference-source EULA: {EULA_URL}"
    )
    caveats.to_csv(path, index=False)


def strip_package_members(root: Path) -> None:
    package_root = root / "embeddings" / "packages"
    for model, members in PACKAGE_MEMBERS_TO_REMOVE.items():
        archive = package_root / f"{model}.zip"
        if not archive.is_file():
            raise FileNotFoundError(archive)
        import zipfile

        with zipfile.ZipFile(archive) as handle:
            existing = set(handle.namelist())
        removable = [member for member in members if member in existing]
        if not removable:
            continue
        print(f"[strip] {archive.name}: {len(removable)} member(s)", flush=True)
        subprocess.run(
            ["/usr/bin/zip", "-q", "-d", str(archive), *removable],
            check=True,
        )


def update_package_manifest(root: Path) -> None:
    manifest_path = root / "metadata" / "embedding_manifest.csv"
    packages_path = root / "metadata" / "model_packages.csv"
    embeddings = pd.read_csv(manifest_path)
    packages = pd.read_csv(packages_path)
    available = embeddings["available"].astype(str).str.lower().isin({"true", "1", "yes"})
    packages["manifest_rows"] = packages.get("manifest_rows", 64)
    packages["synthetic_demo_rows"] = packages.get("synthetic_demo_rows", 1)
    for index, row in packages.iterrows():
        model = str(row["model"])
        subset = embeddings[embeddings["model"].eq(model)]
        full_subset = subset[available.loc[subset.index]]
        package_path = root / str(row["package_path"])
        packages.loc[index, "logical_rows"] = int(len(full_subset))
        packages.loc[index, "unique_artifact_paths"] = int(
            full_subset["artifact_path"].dropna().astype(str).nunique()
        )
        packages.loc[index, "manifest_rows"] = int(len(subset))
        packages.loc[index, "synthetic_demo_rows"] = int((~available.loc[subset.index]).sum())
        packages.loc[index, "size_bytes"] = int(package_path.stat().st_size)
        packages.loc[index, "sha256"] = sha256(package_path)
        existing_note = "" if pd.isna(row.get("notes")) else str(row.get("notes"))
        release_note = (
            "Availability follows the embedding manifest."
        )
        for stale_note in (release_note,):
            existing_note = existing_note.replace(stale_note, "").strip()
        packages.loc[index, "notes"] = " ".join(
            part for part in (existing_note, release_note) if part
        )
    packages.to_csv(packages_path, index=False)


def update_kaggle_metadata(root: Path) -> None:
    path = root / "dataset-metadata.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["licenses"] = [{"name": "CC-BY-4.0"}]
    payload["subtitle"] = (
        "Multi-city urban benchmark with fixed splits and 11 models"
    )
    payload["description"] = (
        "CityRep release with 64 registered city-task entries, 126 fixed split files, "
        "and 11 frozen model embedding packages. The 704-row manifest includes "
        "task-specific availability metadata. "
        "Released under CC BY 4.0; required source credits are documented in the package."
    )
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def sync_code_registries(release_root: Path, code_root: Path) -> None:
    copies = {
        release_root / "data" / "tasks.json": code_root / "data" / "tasks.json",
        release_root / "data" / "registry" / "tasks.csv": (
            code_root / "data" / "registry" / "tasks.csv"
        ),
        release_root / "splits" / "manifest.csv": code_root / "splits" / "manifest.csv",
        release_root / "metadata" / "embedding_manifest.csv": (
            code_root / "baselines" / "registry" / "embedding_manifest.csv"
        ),
        release_root / "metadata" / "landuse_license_caveats.csv": (
            code_root / "metadata" / "landuse_license_caveats.csv"
        ),
        release_root / "metadata" / "model_packages.csv": (
            code_root / "metadata" / "model_packages.csv"
        ),
    }
    for source, target in copies.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def main() -> None:
    args = parse_args()
    root = args.release_root.resolve()
    n_extract = update_task_payload(root)
    update_task_registries(root, n_extract)
    update_splits(root)
    update_embedding_manifest(root)
    update_landuse_caveats(root)
    if args.strip_embedding_archives:
        strip_package_members(root)
    update_package_manifest(root)
    update_kaggle_metadata(root)
    if args.code_root:
        sync_code_registries(root, args.code_root.resolve())
    print(
        json.dumps(
            {
                "task_id": TASK_ID,
                "release_status": "synthetic_demo_only",
                "released_rows": n_extract,
                "full_benchmark_rows": FULL_N_SAMPLES,
                "released_split_files": 0,
                "released_task_embedding_rows": 0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
