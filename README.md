# CityRep

CityRep evaluates frozen urban representations across 8 cities, 8 task types, and 11 models. The public release contains 64 registered city-task entries.

- **Data:** https://www.kaggle.com/datasets/cityrep/cityrep/

## Release contents

- 64 registered city-task payloads with provenance and availability metadata.
- 126 fixed split files with five seeds per protocol.
- 11 model-level embedding packages.
- A 704-row model-city-task manifest with machine-readable availability.
- Evaluation and alignment code, fixed-split generation, exact protocol parameters, notebooks, compact reference results, and checksums.

Task-specific availability is declared in the registries.

## Install

```bash
conda env create -f environment.yml
conda activate urban-benchmark
pip install -e .
```

## Download

Authenticate the Kaggle CLI, then run:

```bash
pip install kaggle
kaggle auth login
./download.sh
```

The full release is downloaded from `cityrep/cityrep` and placed under
`data/tasks/`, `splits/`, and `baselines/artifacts/`.

## Verify

```bash
python -m pytest
python -m urban_benchmark audit

python -m urban_benchmark evaluate \
  --models place2vec \
  --cities london \
  --tasks population \
  --max-runs 1 \
  --device cpu \
  --out-root results/smoke_eval
```

The audit should report 64 registry entries, 126 valid split files, 11 models,
704 manifest rows, and no missing released artifacts. The smoke evaluation
should finish with one result and zero failures.

## Reproduce the public benchmark

```bash
python -m urban_benchmark evaluate \
  --task-registry data/tasks.json \
  --embedding-manifest baselines/registry/embedding_manifest.csv \
  --protocol block10_5seed_mlp1024 \
  --device cuda:0 \
  --out-root results/repro_main_eval

python -m urban_benchmark summarize --result-root results/repro_main_eval
```

Rows marked `available=false` are skipped. The released protocol uses task-specific 10 × 10 spatial blocks, seeds `42, 24, 7, 0, 100`, row-wise L2 embedding normalization, and a one-hidden-layer MLP with 1024 units. Training uses Adam, learning rate `1e-3`, batch size `512`, at most 100 epochs, and early-stopping patience 10.

## Repository layout

- `urban_benchmark/`: evaluator and command-line interface.
- `configs/release/`: evaluation protocols.
- `data/tasks.json`: 64-entry registry with availability metadata.
- `splits/manifest.csv`: 126 released split files.
- `baselines/registry/`: model and embedding manifests; baseline training code is not included.
- `results/` and `notebooks/`: compact reference results and analyses.
- `metadata/`: package manifests, Croissant metadata, audits, and checksums.

## Documentation

- [Quickstart](QUICKSTART.md)
- [Evaluation protocol](docs/EVALUATION_CARD.md)
- [Alignment policy](docs/ALIGNMENT_POLICY.md)
- [Reproducibility](docs/REPRODUCIBILITY.md)
- [Dataset card](docs/DATASET_CARD.md)
- [Licenses and provenance](docs/LICENSES_AND_PROVENANCE.md)
- [Packaging](docs/PACKAGING.md)

## License

Software: [MIT](LICENSE). Released data, splits, frozen embeddings, and metadata:
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See
[Data License and Attribution](DATA_LICENSES.md).
