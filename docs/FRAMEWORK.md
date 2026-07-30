# Benchmark Framework

## Task Registry

All downstream tasks are registered in `data/tasks.json`. A task entry must define:

- `task_id`: `<city>.<task>.<year>`.
- `task_type`: `classification`, `regression`, or `distribution`.
- `source_type`: `samples` or `raster`.
- Label columns and spatial metadata.

Sample tasks are point or polygon-derived units with `x/y` or WKT geometry plus labels. Raster tasks are converted to pixel-center samples at load time.

## Adding A City To An Existing Task

For users extending downstream evaluation to a new city, the preferred entry
point is:

```bash
python -m urban_benchmark extend-city ...
python -m urban_benchmark run-model ...
```

`extend-city` reads a CSV/JSON manifest and builds downstream tasks for one
city. It can use a manually supplied boundary to crop raster labels and it
updates the task registry. Manifest rows may include `download_command` entries
for source-specific downloads; these commands are only executed when the user
passes `--allow-download-commands`. `run-model` evaluates a user-provided
embedding directory on selected city-task pairs. These commands do not require
users to edit embedding manifests by hand.

The manual equivalent is:

1. Create a processed task directory under `data/tasks/<city>.<task>.<year>/`.
2. Write `samples.parquet` for sample tasks, or a task raster plus `task.json` for raster tasks.
3. Add the task entry to `data/tasks.json`.
4. Evaluate a user-provided model with `run-model`, or add embedding rows to an embedding manifest.

## Adding A New Task

New tasks should use one of the three supported task types:

- `classification`: integer class labels.
- `regression`: one continuous label column, optionally normalized by the loader.
- `distribution`: multiple label columns that are renormalized row-wise.

The benchmark does not require tasks to be on the same grid. Raster labels, point labels, and polygon-derived samples are all valid.

## Input Embeddings

Supported embedding source types:

- `region_table`: region embeddings, H3 by default.
- `raster`: multi-band raster embeddings.
- `point_table`: embeddings generated directly at task point coordinates.

For region embeddings from irregular source units, export to H3 first. Raster embeddings should remain as rasters: use matched-cell lookup on the task grid, area-mean alignment for a different raster task grid, or coordinate sampling only for sample tasks without a task grid.

## Scope Of Automatic Extension

The public benchmark automates downstream task construction through
`extend-city` and model evaluation through `run-model`. Source downloads can be
plugged in through manifest-level `download_command` rows, but source-specific
credentials, accepted-license workflows, and city-specific land-use acquisition
remain outside the benchmark runner. Users do not need to reproduce all
released baselines for a new city; they can evaluate their own raster, region, or
entity embeddings with `run-model`. For additional appendix baselines, globally
available raster embeddings such as AlphaEarth and TESSERA can be generated
locally after the task files have been prepared.

## Evaluation

The reference protocol is `block10_5seed_mlp1024`:

- spatial block split: 10 x 10 blocks.
- test ratio: 0.2.
- validation ratio on train: 0.1.
- seeds: 42, 24, 7, 0, 100.
- predictor: one-hidden-layer MLP with 1024 hidden units.
- early stopping: validation loss patience 10.
