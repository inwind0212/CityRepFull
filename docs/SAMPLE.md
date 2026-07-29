# Embedding Sample

The sample is the unmodified Singapore AlphaEarth embedding aligned to the
PM2.5 task. It was selected because its 64-band GeoTIFF is compact (less than
1 MB) while retaining the raster structure used by the full release.

Download and validate it with:

```bash
bash download_sample.sh
```

The validator checks the SHA-256 digest, file size, shape, data type, CRS, and
bounds against `metadata/sample_embedding.json`.

The sample demonstrates the embedding format only. Download the full release
to run benchmark evaluation.
