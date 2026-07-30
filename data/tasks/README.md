# Task Data Directory

This directory is populated from the canonical `cityrep/cityrep` Kaggle dataset.

Expected layout:

```text
data/tasks/<task_id>/samples.parquet
data/tasks/<task_id>/task.json
data/tasks/<task_id>/labels.tif        # when the task has a raster label source
```

The canonical 8-city benchmark registry is `data/tasks.json`. The CSV version is `data/registry/tasks.csv`.
