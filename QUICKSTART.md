# Quickstart

## Install

```bash
conda env create -f environment.yml
conda activate urban-benchmark
pip install -e .
```

## Download

```bash
pip install kaggle
kaggle auth login
./download.sh
```

## Test the release

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

A successful audit reports:

- 64 registry entries;
- 126 valid split files;
- 11 model packages;
- 704 manifest rows with availability metadata;
- zero missing released artifacts and zero failures.

## Run the spatial benchmark

```bash
python -m urban_benchmark evaluate \
  --task-registry data/tasks.json \
  --embedding-manifest baselines/registry/embedding_manifest.csv \
  --protocol block10_5seed_mlp1024 \
  --device cuda:0 \
  --out-root results/repro_main_eval
```

The evaluator follows the availability field in the manifest. See [Evaluation Card](docs/EVALUATION_CARD.md) and [Alignment Policy](docs/ALIGNMENT_POLICY.md).
