# Model packages

The 11 ZIP packages are hosted at https://www.kaggle.com/datasets/cityrep/cityrep/ and are not committed to GitHub. `metadata/model_packages.csv` records their extraction prefixes, logical-row counts, sizes, and checksums. `./download.sh all` downloads and extracts them into `baselines/artifacts/`.

The archives contain the frozen embedding values used by the main benchmark. Native AETHER rows and native AlphaEarth land-use rows are distributed as exact, unnormalized, `sample_id`-keyed Parquet tables with alignment reports; the release manifest points to these tables. No raw training inputs, downstream predictions, non-release experimental artifacts, or artifacts outside the canonical task set are included.
