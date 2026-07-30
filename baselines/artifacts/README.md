# Embedding Directory

This directory is populated from the 11 model directories in the canonical
`cityrep/cityrep` Kaggle dataset.

Expected layout:

```text
baselines/artifacts/<model>/<city>/...
```

The required released files are listed in `baselines/registry/embedding_manifest.csv`. These are processed embedding exports used by the benchmark evaluator; raw upstream model-training data are not required for reproducing the reference results.
