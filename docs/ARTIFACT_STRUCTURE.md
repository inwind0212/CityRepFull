# Artifact Structure

## Code repository

| Path | Contents |
|---|---|
| `urban_benchmark/` | Evaluator and command-line interface. |
| `configs/release/` | Evaluation protocols. |
| `data/` | Task registries and placeholders. |
| `splits/` | Split manifest and format documentation. |
| `baselines/registry/` | Model and embedding manifests; model-training code is not included. |
| `results/` | Compact reference tables and figures. |
| `notebooks/` | Analysis notebooks. |
| `metadata/` | Audits, release metadata, Croissant metadata, and checksums. |
| `download_sample.sh` | Downloads and validates the representative embedding sample. |

## Hosted assets

- `cityrep_sample/`: representative Singapore AlphaEarth embedding sample.
- `cityrep_core/data/tasks/`: 64 registered task payloads.
- `cityrep_core/splits/`: 126 fixed split files.
- `embeddings/`: frozen artifacts grouped into 11 model directories.

`download.sh` restores hosted files into paths referenced by the manifests.
Evaluation outputs, aligned caches, predictions, checkpoints, and logs are
generated locally and excluded from the release.
