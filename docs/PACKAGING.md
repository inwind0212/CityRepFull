# Packaging

## GitHub

The code repository contains evaluation code, configurations, registries, compact results, notebooks, documentation, and manifests. Large task payloads, split payloads, and embedding bytes are hosted separately.

## Kaggle

The canonical `cityrep/cityrep` dataset contains:

- `cityrep_core/`: task data, fixed splits, metadata, and checksums;
- `embeddings/`: 11 model directories and their package manifest.

`download.sh` restores the documented repository paths. The package manifest,
split manifest, and release checksums contain sizes and SHA-256 values. The
704-row embedding manifest records task-specific availability.

The release excludes raw source downloads, credentials, training corpora, checkpoints, prediction dumps, caches, and the restricted Verisk-derived London task.

## Croissant

Regenerate and validate `metadata/croissant/cityrep.json` with:

```bash
python scripts/create_croissant_metadata.py
mlcroissant validate --jsonld=metadata/croissant/cityrep.json
mlcroissant load --jsonld=metadata/croissant/cityrep.json \
  --record_set=release-components --num_records=5
```
