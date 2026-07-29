# Model embeddings

The Kaggle dataset exposes frozen artifacts under `embeddings/<model>/`; the
large files are not committed to GitHub. `metadata/model_directories.csv`
records the distribution paths, install prefixes, file counts, sizes, and
directory-tree checksums.
`bash download.sh` restores the files under `baselines/artifacts/`.

The model directories contain the frozen embedding values used by the main benchmark. Native AETHER rows and native AlphaEarth land-use rows are distributed as exact, unnormalized, `sample_id`-keyed Parquet tables with alignment reports; the release manifest points to these tables. No raw training inputs, downstream predictions, non-release experimental artifacts, or artifacts outside the canonical task set are included.
