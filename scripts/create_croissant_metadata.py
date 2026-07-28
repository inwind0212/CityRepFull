#!/usr/bin/env python3
# Create the canonical CityRep Croissant 1.1 and Responsible AI metadata.

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARD_CONTEXT = {
    "@language": "en",
    "@vocab": "https://schema.org/",
    "arrayShape": "cr:arrayShape",
    "citeAs": "cr:citeAs",
    "column": "cr:column",
    "conformsTo": "dct:conformsTo",
    "containedIn": "cr:containedIn",
    "cr": "http://mlcommons.org/croissant/",
    "rai": "http://mlcommons.org/croissant/RAI/",
    "prov": "http://www.w3.org/ns/prov#",
    "data": {"@id": "cr:data", "@type": "@json"},
    "dataType": {"@id": "cr:dataType", "@type": "@vocab"},
    "dct": "http://purl.org/dc/terms/",
    "description": {"@container": "@language"},
    "equivalentProperty": "cr:equivalentProperty",
    "examples": {"@id": "cr:examples", "@type": "@json"},
    "extract": "cr:extract",
    "field": "cr:field",
    "fileProperty": "cr:fileProperty",
    "fileObject": "cr:fileObject",
    "fileSet": "cr:fileSet",
    "format": "cr:format",
    "includes": "cr:includes",
    "isArray": "cr:isArray",
    "isLiveDataset": "cr:isLiveDataset",
    "jsonPath": "cr:jsonPath",
    "key": "cr:key",
    "md5": "cr:md5",
    "name": {"@container": "@language"},
    "parentField": "cr:parentField",
    "path": "cr:path",
    "recordSet": "cr:recordSet",
    "references": "cr:references",
    "regex": "cr:regex",
    "repeated": "cr:repeated",
    "replace": "cr:replace",
    "samplingRate": "cr:samplingRate",
    "sc": "https://schema.org/",
    "separator": "cr:separator",
    "source": "cr:source",
    "subField": "cr:subField",
    "transform": "cr:transform",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-registry", type=Path, default=ROOT / "data" / "tasks.json")
    parser.add_argument("--embedding-manifest", type=Path, default=ROOT / "baselines" / "registry" / "embedding_manifest.csv")
    parser.add_argument("--hosted-url", default="https://www.kaggle.com/datasets/cityrep/cityrep/")
    parser.add_argument("--download-url", default="https://www.kaggle.com/api/v1/datasets/download/cityrep/cityrep")
    parser.add_argument("--code-url", default="")
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--date-published", default="2026-07-28")
    parser.add_argument("--out", type=Path, default=ROOT / "metadata" / "croissant" / "cityrep.json")
    return parser.parse_args()


def component_record(component: str, path_pattern: str, count: int, description: str) -> dict:
    prefix = "release-components"
    return {
        f"{prefix}/component": component,
        f"{prefix}/path_pattern": path_pattern,
        f"{prefix}/count": count,
        f"{prefix}/description": description,
    }


def main() -> None:
    args = parse_args()
    registry = json.loads(args.task_registry.read_text())
    tasks = registry.get("tasks", registry)
    cities = sorted({str(spec.get("city", task_id.split(".")[0])) for task_id, spec in tasks.items()})
    task_names = sorted({str(spec.get("task", task_id.split(".")[1])) for task_id, spec in tasks.items()})
    full_task_count = sum(
        str(spec.get("availability", "full")) == "full" for spec in tasks.values()
    )
    synthetic_demo_count = sum(
        str(spec.get("availability", "full")) == "synthetic_demo_only"
        for spec in tasks.values()
    )
    model_count = 11
    embedding_rows = len(tasks) * model_count
    available_embedding_rows = full_task_count * model_count

    container = {"@id": "cityrep-download"}
    distributions = [
        {
            "@type": "cr:FileObject",
            "@id": "cityrep-download",
            "name": "cityrep.zip",
            "description": "Download archive for the current Kaggle dataset version.",
            "contentUrl": args.download_url,
            "encodingFormat": "application/zip",
        },
        {
            "@type": "cr:FileSet",
            "@id": "task-payloads",
            "name": "task payloads",
            "description": "Processed sample tables, task metadata, and label rasters.",
            "containedIn": container,
            "includes": ["data/tasks/**"],
            "encodingFormat": ["application/json", "application/x-parquet", "image/tiff"],
        },
        {
            "@type": "cr:FileSet",
            "@id": "fixed-splits",
            "name": "fixed splits",
            "description": "Spatial and random partitions with five seeds, keyed by sample_id.",
            "containedIn": container,
            "includes": ["splits/**/*.json.gz"],
            "encodingFormat": "application/gzip",
        },
        {
            "@type": "cr:FileSet",
            "@id": "model-packages",
            "name": "model embedding packages",
            "description": "Frozen embeddings grouped into 11 model packages.",
            "containedIn": container,
            "includes": ["embeddings/packages/*.zip"],
            "encodingFormat": "application/zip",
        },
        {
            "@type": "cr:FileObject",
            "@id": "task-registry",
            "name": "tasks.json",
            "contentUrl": "data/tasks.json",
            "containedIn": container,
            "encodingFormat": "application/json",
        },
        {
            "@type": "cr:FileObject",
            "@id": "embedding-manifest",
            "name": "embedding_manifest.csv",
            "contentUrl": "metadata/embedding_manifest.csv",
            "containedIn": container,
            "encodingFormat": "text/csv",
        },
        {
            "@type": "cr:FileObject",
            "@id": "split-manifest",
            "name": "manifest.csv",
            "contentUrl": "splits/manifest.csv",
            "containedIn": container,
            "encodingFormat": "text/csv",
        },
    ]

    fields = [
        ("component", "sc:Text", "Release component identifier."),
        ("path_pattern", "sc:Text", "Path or glob pattern inside the Kaggle archive."),
        ("count", "sc:Integer", "Number of logical files or manifest rows."),
        ("description", "sc:Text", "Component contents."),
    ]
    record_set = {
        "@type": "cr:RecordSet",
        "@id": "release-components",
        "name": "release components",
        "description": "Dataset-level inventory for the hierarchical benchmark release.",
        "key": {"@id": "release-components/component"},
        "field": [
            {
                "@type": "cr:Field",
                "@id": f"release-components/{field_id}",
                "name": field_id,
                "description": description,
                "dataType": data_type,
            }
            for field_id, data_type, description in fields
        ],
        "data": [
            component_record("task-payloads", "data/tasks/**", len(tasks), "Registered task payloads with task-level availability metadata."),
            component_record("spatial-splits", "splits/block10_5seed_mlp1024/*.json.gz", full_task_count, "Fixed spatial partitions for registered evaluation tasks."),
            component_record("random-splits", "splits/random_5seed_mlp1024/*.json.gz", full_task_count, "Fixed random diagnostic partitions for registered evaluation tasks."),
            component_record("model-packages", "embeddings/packages/*.zip", model_count, "Model-level embedding archives."),
            component_record("embedding-index", "metadata/embedding_manifest.csv", embedding_rows, "Model-city-task index with task-specific availability metadata."),
        ],
    }

    payload = {
        "@context": STANDARD_CONTEXT,
        "@type": "sc:Dataset",
        "name": "CityRep Multi-City Urban Representation Benchmark",
        "description": (
            "CityRep contains 64 registered city-task entries across eight cities and eight "
            "task types, 126 fixed split files, and frozen embeddings grouped into 11 "
            "model packages. The 704-row manifest records task-specific availability."
        ),
        "conformsTo": "http://mlcommons.org/croissant/1.1",
        "isLiveDataset": True,
        "url": args.hosted_url,
        "version": args.version,
        "datePublished": args.date_published,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "citeAs": "CityRep benchmark release, version 1.0.0.",
        "citation": "CityRep benchmark release, version 1.0.0.",
        "creator": {"@type": "sc:Organization", "name": "CityRep maintainers"},
        "publisher": {"@type": "sc:Organization", "name": "CityRep maintainers"},
        "keywords": ["urban computing", "geospatial embeddings", "spatial machine learning", "benchmark", "remote sensing"],
        "spatialCoverage": [{"@type": "sc:Place", "name": city.replace("_", " " ).title()} for city in cities],
        "variableMeasured": task_names,
        "distribution": distributions,
        "recordSet": [record_set],
        "rai:hasSyntheticData": True,
        "rai:dataCollection": "Task labels are processed from documented spatial sources. The London land-use payload is synthetic; its source-based reference task is not redistributed. Frozen embeddings are exported from the documented representation models.",
        "rai:dataPreprocessingProtocol": ["Task construction and filtering are recorded in each task.json and docs/RAW_DATA_SOURCES.md. Fixed partitions are keyed by sample_id and checked for completeness and disjointness."],
        "rai:dataAnnotationProtocol": ["For the seven released source-based land-use tasks, source classes are mapped to the released 12-class taxonomy and audited in the mapping tables. The London schema demo uses two artificial rows per class and is not an evaluation task. Other task labels are derived from the cited gridded or vector source products."],
        "rai:dataBiases": ["Coverage, label quality, update cycle, spatial resolution, and semantics vary by city and source. Street-view and POI inputs may underrepresent some neighborhoods."],
        "rai:dataUseCases": ["Urban representation benchmarking", "Spatial split diagnostics", "Multi-city task evaluation"],
        "rai:dataLimitations": ["The eight cities are not globally representative. Land-use taxonomies are harmonized. Four age-distribution cities are excluded from reference aggregation because of source-quality concerns. Required source credits are recorded with each task.", "The dataset is not suitable for individual profiling, high-stakes allocation, causal claims, or deployment without local validation."],
        "rai:dataSocialImpact": "The release can support transparent comparison of urban representations, but uncritical use may reproduce geographic coverage and source-data biases. It must not be treated as a direct decision system for people or neighborhoods.",
        "rai:personalSensitiveInformation": ["No person-level records are redistributed. Coordinates identify gridded or task samples rather than individuals. Raw street-view images and raw POI dumps are excluded."],
        "rai:dataReleaseMaintenancePlan": "Corrections should be issued as versioned Kaggle dataset releases with updated checksums, metadata, and release notes.",
        "prov:wasDerivedFrom": [
            "https://hub.worldpop.org/",
            "https://doi.org/10.5281/zenodo.18429133",
            "https://eogdata.mines.edu/products/vnl/",
            "https://doi.org/10.7927/as2r-9p42",
            "https://www.openstreetmap.org/",
            "https://doi.org/10.5067/MODIS/MOD11A2.061",
        ],
        "prov:wasGeneratedBy": [
            {"@type": "prov:Activity", "name": "CityRep task preprocessing", "description": "Source-specific cleaning, harmonization, sampling, and label construction recorded in task metadata."},
            {"@type": "prov:Activity", "name": "CityRep split generation", "description": "Deterministic spatial and random partitions generated from stable sample identifiers with five fixed seeds."},
            {"@type": "prov:Activity", "name": "CityRep embedding export", "description": "Frozen model outputs exported to raster, region-table, point-table, or entity-table representations."},
            {"@type": "prov:Activity", "name": "London synthetic schema demo generation", "description": "No random seed or source records are used. scripts/make_london_synthetic_demo.py deterministically creates two artificial rows per released class from fixed coordinate constants and sequential synthetic identifiers."},
        ],
    }
    if args.code_url:
        payload["sameAs"] = args.code_url

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(args.out)


if __name__ == "__main__":
    main()
