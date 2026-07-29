# Dataset Card: CityRep

## Summary

CityRep compares frozen urban representations across eight cities, eight task types, and heterogeneous spatial supports. The public release contains 64 registered city-task entries and frozen embeddings grouped into 11 model directories.

Cities: London, New York, Singapore, Sydney, Mumbai, Nairobi, Jakarta, and Cape Town.

Tasks: land-use classification; road-density, population, GDP, nighttime-light, PM2.5, and daytime-LST regression; and age-distribution prediction.

## Hosted assets

- `cityrep_sample/`: one representative Singapore AlphaEarth embedding with
  metadata and a checksum.
- `cityrep_core/data/tasks/`: 64 registered payloads with task-level availability metadata.
- `cityrep_core/data/tasks.json` and `cityrep_core/data/registry/tasks.csv`: 64-entry registries with availability metadata.
- `cityrep_core/splits/`: 126 fixed split files, each with five seeds.
- `embeddings/`: frozen artifacts grouped into 11 model directories.
- Manifests, checksums, source/licence notes, and Croissant/RAI metadata.

The embedding manifest contains 704 logical model-city-task rows with an explicit availability field.
The sample is an unmodified copy of one artifact from the full release and is
provided for format inspection, not benchmark evaluation.

## London disclosure

The London land-use payload is a synthetic schema example. The source-based reference task used for aggregate results is not included.

## Intended use

The release supports scientific comparison of urban representations under a common alignment, split, and downstream-head protocol. CityRep is not intended for individual profiling, planning enforcement, policing, eligibility, resource allocation, or other high-stakes decisions.

## Data and splits

Each task directory contains `samples.parquet` and `task.json`; raster-derived tasks also include `labels.tif`. Stable `sample_id` values connect complete tasks, fixed splits, embeddings, and predictions. The main split uses task-specific 10 × 10 spatial blocks with seeds `42, 24, 7, 0, 100`; a random split is included as a diagnostic.

## Licences

Released data, splits, frozen embeddings, metadata, and synthetic examples use
CC BY 4.0. Required source credits are listed in `DATA_LICENSES.md` and each
`task.json`. Raw upstream inputs and the restricted London reference task are
not included.

## Limitations

- Eight cities are not globally representative.
- Source resolution, update cycle, coverage, and semantics differ by city.
- Land-use classes are harmonized from heterogeneous local taxonomies.
- Age-distribution aggregation excludes Mumbai, Nairobi, Jakarta, and Cape Town because of source-quality limitations.
- Scores measure predictive utility under this protocol, not causal or deployment validity.
