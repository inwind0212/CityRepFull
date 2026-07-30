# Alignment Policy

## Runtime rule

Every model is evaluated on the sample IDs and coordinates registered for the downstream task. Runtime behavior is:

- Raster on the exact task grid: row/column lookup with no resampling.
- Raster finer than a raster-backed task grid: area-weighted mean within each task cell. `max` pooling is available as an explicit alternative.
- Raster coarser than a raster-backed task grid: the source-cell embedding is shared by the task cells it covers.
- Raster used with a sample task that has no task grid: sample at task coordinates after CRS transformation.
- H3/region table: task coordinates or registered region IDs are mapped to the region table.
- Point/entity table: stable ID lookup when IDs exist; otherwise the registered point rule is used.
- Coordinate encoder: embeddings are exported by querying the task coordinates.

For raster-backed regression and distribution tasks, `method=auto` implements these rules by reprojecting each embedding band to the registered label grid. The released protocols set `pooling=mean`; users can select `--pooling max`. Coordinate sampling is not used as a substitute for aggregation when a task grid is available.

Several released raster artifacts were already materialized on a task grid by their export scripts. They follow the first rule and are not pooled again; the manifest path, artifact metadata, and filename commonly record `_mean` or `taskgrid`.

For download size only, native AETHER rows and native AlphaEarth land-use rows are materialized once with this runtime policy and stored as `sample_id`-keyed entity tables. These tables contain the exact float values before row-wise L2 normalization; they do not change pooling, interpolation, splits, labels, or the downstream head. Their per-task alignment reports are included with the model artifacts. The release manifest selects these tables directly, so users do not need the hundreds of GiB of unused city-wide pixels.

## Model-specific sources

- **PE:** deterministic Sphere2Vec-sphereC positional features at task coordinates.
- **Space2Vec and CaLLiPer:** coordinate encoder outputs queried/exported at task units.
- **SatCLIP:** coordinate/remote-sensing representation exported at task units.
- **Place2Vec:** H3 resolution-8 POI region table and H3 lookup.
- **CityFM:** H3 resolution-8 POI/OSM region table and H3 lookup.
- **Urban2Vec:** street-view plus POI region embeddings; no remote-sensing input.
- **MuseCL:** street-view, remote-sensing, and POI region embeddings.
- **TESSERA:** native reference-grid or pre-materialized task-grid rasters as recorded in the manifest.
- **AlphaEarth:** pre-materialized task-grid rasters, plus sample-aligned native values for land-use.
- **AETHER:** pre-materialized task-grid rasters, plus sample-aligned native-raster values where the main experiment sampled the city raster directly.

No representation may borrow a population target grid as the support for the nighttime-light or land-use task. The released manifest is the authoritative row-level policy.
