# Reproducibility

CityRep uses two coordinated releases:

1. The GitHub repository: code, configurations, registries, documentation, notebooks, and compact results.
2. The `cityrep/cityrep` Kaggle dataset: 64 registered task payloads, 126 fixed split files, and frozen embeddings grouped into 11 model directories.

After `bash download.sh`, run:

```bash
python -m pytest
python -m urban_benchmark audit
```

Expected counts are 64 registry entries, 11 models, 704 manifest rows, and 126 fixed split files. Availability is recorded in the registries.

The evaluator follows the manifest availability field. Compact result tables may include aggregate reference results whose restricted source records are not redistributed.

The released protocol uses fixed splits, row-wise L2 embedding normalization, a one-hidden-layer 1024-unit MLP, Adam with learning rate `1e-3`, batch size 512, at most 100 epochs, and early-stopping patience 10. See `docs/EVALUATION_CARD.md` for details.

For a quick format check without the full download, run
`bash download_sample.sh`. The representative sample is not used to reproduce
benchmark scores.
