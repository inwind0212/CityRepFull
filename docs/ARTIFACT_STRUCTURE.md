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
| `metadata/` | Audits, package metadata, Croissant metadata, and checksums. |

## Hosted assets

- `data/tasks/`: 64 registered task payloads.
- `splits/`: 126 fixed split files.
- `embeddings/packages/`: 11 model-level archives.

Archives extract into paths referenced by the manifests. Evaluation outputs, aligned caches, predictions, checkpoints, and logs are generated locally and excluded from the release.
