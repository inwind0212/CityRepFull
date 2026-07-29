# Licenses and Provenance

This file summarizes the processed public release. Per-task `task.json` files and `DATA_LICENSES.md` are authoritative for source-specific terms.

## Included

- 64 registered processed task payloads with availability metadata.
- Registries, metadata, fixed splits, compact results, and figures.
- Frozen embeddings grouped into 11 model directories.

Software is MIT. Released data, splits, frozen embeddings, metadata, and
synthetic examples are CC BY 4.0. Baseline training and upstream model code are
not included.

## Excluded

- The 100,000-row Verisk-derived London reference task, its splits, and its sample-aligned embeddings.
- Raw street-view images, raw POI dumps, upstream training corpora, credentials, caches, and checkpoints.

## Source-level notes

- WorldPop and Kummu GDP: CC BY 4.0.
- VIIRS nighttime lights: public domain.
- OpenStreetMap road-density derivatives: ODbL 1.0 with attribution.
- MODIS LST: NASA/LP DAAC terms and DOI citation.
- SEDAC PM2.5: CIESIN open-data policy and DOI citation.
- Land use: processed city tasks with documented source attribution; raw tiles
  and polygons are excluded.

Preserve the source attribution recorded with each task.
