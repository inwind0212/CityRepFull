"""Build the 11 model-level CityRep embedding archives.

The input source map is intentionally local and is not part of the public
release. It maps each public ``artifact_path`` to the corresponding frozen
file on the packaging machine.

Very large native AETHER and AlphaEarth city rasters are converted to
task-specific, sample-id keyed Parquet tables. The conversion uses the same
alignment implementation as evaluation, without L2 normalization. This keeps
the benchmark inputs exact while avoiding a roughly 350 GiB redistribution of
city-wide source rasters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile

import pandas as pd

from urban_benchmark.align import align_embedding
from urban_benchmark.embeddings import RasterEmbedding
from urban_benchmark.tasks import load_task


SAMPLE_ALIGNED_ROLES = {
    "native_aether_raster",
    "native_alphaearth_raster",
}
EXPECTED_TASKS = {
    "age_distribution",
    "gdp",
    "landuse",
    "lst_day_mean",
    "nightlight",
    "pm25",
    "population",
    "road_density",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--source-map", required=True, type=Path)
    parser.add_argument("--task-registry", required=True, type=Path)
    parser.add_argument("--package-manifest", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--release-manifest-out", required=True, type=Path)
    parser.add_argument("--release-package-manifest-out", required=True, type=Path)
    parser.add_argument(
        "--compression",
        choices=["stored", "deflated"],
        default="stored",
        help="Stored is recommended because GeoTIFF and Parquet inputs are already compressed.",
    )
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def _sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _source_lookup(source_map_path: Path) -> dict[str, Path]:
    table = pd.read_csv(source_map_path)
    source_column = "local_source_path" if "local_source_path" in table.columns else "source"
    required = {"artifact_path", source_column}
    missing = required - set(table.columns)
    if missing:
        raise ValueError(f"Source map is missing columns: {sorted(missing)}")
    if table["artifact_path"].duplicated().any():
        duplicates = table.loc[table["artifact_path"].duplicated(), "artifact_path"].tolist()
        raise ValueError(f"Source map has duplicate artifact paths: {duplicates[:5]}")
    lookup = {
        str(row.artifact_path): Path(str(getattr(row, source_column))).expanduser()
        for row in table.itertuples(index=False)
    }
    missing_files = [f"{artifact}: {path}" for artifact, path in lookup.items() if not path.is_file()]
    if missing_files:
        raise FileNotFoundError("Missing mapped source files:\n" + "\n".join(missing_files[:20]))
    return lookup


def _embedding_columns(dim: int) -> list[str]:
    width = max(3, len(str(max(0, dim - 1))))
    return [f"embedding_{index:0{width}d}" for index in range(dim)]


def _sample_aligned_path(row: pd.Series) -> str:
    return (
        Path("baselines")
        / "artifacts"
        / str(row["model"])
        / str(row["city"])
        / f"{row['task_id']}_{row['model']}_sample_aligned.parquet"
    ).as_posix()


def _materialize_sample_aligned(
    row: pd.Series,
    source: Path,
    task_registry: Path,
    work_dir: Path,
) -> tuple[Path, Path, dict[str, object]]:
    artifact_path = _sample_aligned_path(row)
    output = work_dir / artifact_path
    report_path = output.with_suffix(".alignment.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    task = load_task(str(row["task_id"]), task_registry)
    aligned = align_embedding(
        task,
        RasterEmbedding(str(row["model_label"]), str(source)),
        normalize=False,
    )
    if aligned.sample_ids != task.samples["sample_id"].astype(str).tolist():
        raise ValueError(f"Sample order changed while materializing {row['task_id']}")

    points = task.samples
    if points.crs is None:
        raise ValueError(f"Task {row['task_id']} has no CRS")
    points_wgs84 = points.to_crs("EPSG:4326")
    columns = _embedding_columns(int(aligned.X.shape[1]))
    table = pd.DataFrame(aligned.X, columns=columns)
    table.insert(0, "y", points_wgs84.geometry.y.to_numpy())
    table.insert(0, "x", points_wgs84.geometry.x.to_numpy())
    table.insert(0, "sample_id", aligned.sample_ids)
    table.to_parquet(output, index=False, compression="zstd")

    report = {
        **aligned.report,
        "release_artifact_path": artifact_path,
        "release_representation": "sample_id_keyed_entity_table",
        "stored_l2_normalized": False,
        "source_size_bytes": source.stat().st_size,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output, report_path, report


def _updated_sample_row(
    row: pd.Series,
    artifact_path: str,
    embedding_dim: int,
) -> pd.Series:
    config = {
        "name": str(row["model_label"]),
        "path": artifact_path,
        "type": "entity",
        "entity_id_col": "sample_id",
        "task_entity_id_col": "sample_id",
        "x_col": "x",
        "y_col": "y",
        "crs": "EPSG:4326",
        "embedding_dim": int(embedding_dim),
    }
    row = row.copy()
    row["embedding_path"] = artifact_path
    row["artifact_path"] = artifact_path
    row["embedding_source_type"] = "entity"
    row["embedding_config"] = json.dumps(config, sort_keys=True)
    row["source_role"] = f"sample_aligned_{row['source_role']}_table"
    row["alignment_policy"] = (
        "sample_id lookup in a benchmark-ready table produced by the released "
        "raster alignment policy; values are stored before row-wise L2 normalization"
    )
    row["path_exists"] = False
    return row


def _zip_member(
    archive: zipfile.ZipFile,
    source: Path,
    artifact_path: str,
    compression: int,
) -> None:
    archive.write(source, arcname=artifact_path, compress_type=compression)


def main() -> None:
    args = _parse_args()
    manifest = pd.read_csv(args.manifest)
    packages = pd.read_csv(args.package_manifest)
    sources = _source_lookup(args.source_map)

    if len(manifest) != 704:
        raise ValueError(f"Expected 704 logical manifest rows, found {len(manifest)}")
    if manifest["model"].nunique() != 11:
        raise ValueError(f"Expected 11 models, found {manifest['model'].nunique()}")
    if manifest[["model", "city", "task"]].duplicated().any():
        raise ValueError("Embedding manifest contains duplicate model/city/task rows")
    if packages["model"].nunique() != 11 or len(packages) != 11:
        raise ValueError("Model package manifest must contain exactly 11 models")
    observed_tasks = set(manifest["task"].astype(str))
    if observed_tasks != EXPECTED_TASKS:
        raise ValueError(
            "Embedding manifest task set mismatch: "
            f"expected {sorted(EXPECTED_TASKS)}, found {sorted(observed_tasks)}"
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.work_dir.mkdir(parents=True, exist_ok=True)
    args.release_manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.release_package_manifest_out.parent.mkdir(parents=True, exist_ok=True)

    compression = (
        zipfile.ZIP_STORED if args.compression == "stored" else zipfile.ZIP_DEFLATED
    )
    release_rows: list[pd.Series] = []
    package_results: dict[str, dict[str, object]] = {}

    for package_row in packages.itertuples(index=False):
        model = str(package_row.model)
        model_rows = manifest.loc[manifest["model"].astype(str).eq(model)].copy()
        if len(model_rows) != 64:
            raise ValueError(f"Expected 64 logical rows for {model}, found {len(model_rows)}")

        final_zip = args.out_dir / f"{model}.zip"
        partial_zip = final_zip.with_suffix(".zip.partial")
        if final_zip.exists() and not args.force:
            raise FileExistsError(f"Package already exists: {final_zip}")
        if partial_zip.exists():
            if not args.force:
                raise FileExistsError(f"Partial package already exists: {partial_zip}")
            partial_zip.unlink()

        written: set[str] = set()
        model_release_rows: list[pd.Series] = []
        with zipfile.ZipFile(
            partial_zip,
            mode="w",
            compression=compression,
            allowZip64=True,
        ) as archive:
            for _, row in model_rows.iterrows():
                source_role = str(row["source_role"])
                original_artifact = str(row["artifact_path"])
                source = sources.get(original_artifact)
                if source is None:
                    raise KeyError(f"No source-map row for {original_artifact}")

                if source_role in SAMPLE_ALIGNED_ROLES:
                    aligned_path, report_path, report = _materialize_sample_aligned(
                        row,
                        source,
                        args.task_registry,
                        args.work_dir,
                    )
                    artifact_path = _sample_aligned_path(row)
                    report_artifact = str(Path(artifact_path).with_suffix(".alignment.json"))
                    _zip_member(archive, aligned_path, artifact_path, compression)
                    _zip_member(archive, report_path, report_artifact, compression)
                    written.add(artifact_path)
                    written.add(report_artifact)
                    row = _updated_sample_row(
                        row,
                        artifact_path,
                        int(report["embedding_dim"]),
                    )
                else:
                    artifact_path = original_artifact
                    if artifact_path not in written:
                        _zip_member(archive, source, artifact_path, compression)
                        written.add(artifact_path)
                model_release_rows.append(row)

            model_release_frame = pd.DataFrame(model_release_rows)
            package_note = {
                "model": model,
                "model_label": str(model_rows["model_label"].iloc[0]),
                "logical_model_city_task_rows": 64,
                "manifest_artifact_paths": int(
                    model_release_frame["artifact_path"].nunique()
                ),
                "archive_members_including_alignment_reports": len(written) + 1,
                "sample_aligned_roles": sorted(
                    set(model_rows["source_role"]).intersection(SAMPLE_ALIGNED_ROLES)
                ),
                "stored_embedding_values_l2_normalized": False,
                "evaluation_applies_row_wise_l2_normalization": True,
            }
            archive.writestr(
                f"baselines/artifacts/{model}/PACKAGE.json",
                json.dumps(package_note, indent=2),
                compress_type=compression,
            )

        os.replace(partial_zip, final_zip)
        model_release = pd.DataFrame(model_release_rows)
        release_rows.extend(model_release_rows)
        package_results[model] = {
            "size_bytes": final_zip.stat().st_size,
            "sha256": _sha256(final_zip),
            "unique_artifact_paths": int(model_release["artifact_path"].nunique()),
        }
        print(
            f"[package] {model}: {final_zip.stat().st_size / 2**30:.2f} GiB, "
            f"{package_results[model]['unique_artifact_paths']} manifest artifacts"
        )

    release_manifest = pd.DataFrame(release_rows)[manifest.columns]
    if len(release_manifest) != 704:
        raise ValueError(f"Release manifest row count changed to {len(release_manifest)}")
    release_manifest.to_csv(args.release_manifest_out, index=False)

    release_packages = packages.copy()
    release_packages["size_bytes"] = pd.array(release_packages["size_bytes"], dtype="Int64")
    release_packages["sha256"] = release_packages["sha256"].astype("string")
    for index, row in release_packages.iterrows():
        result = package_results[str(row["model"])]
        release_packages.at[index, "size_bytes"] = int(result["size_bytes"])
        release_packages.at[index, "sha256"] = str(result["sha256"])
        release_packages.at[index, "unique_artifact_paths"] = int(
            result["unique_artifact_paths"]
        )
    release_packages.to_csv(args.release_package_manifest_out, index=False)
    print(f"[manifest] {args.release_manifest_out}")
    print(f"[packages] {args.release_package_manifest_out}")


if __name__ == "__main__":
    main()
