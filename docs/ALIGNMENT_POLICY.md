# Alignment Policy

## Runtime rule

Every model is evaluated on the sample IDs and coordinates registered for the downstream task. Runtime behavior is:

- Raster on the exact task grid: row/column lookup.
- Raster on another grid: sample at task coordinates after CRS transformation.
- H3/region table: task coordinates or registered region IDs are mapped to the region table.
- Point/entity table: stable ID lookup when IDs exist; otherwise the registered point rule is used.
- Coordinate encoder: embeddings are exported by querying the task coordinates.

The evaluator does not apply a universal runtime mean-pooling operation. Several released raster artifacts were pre-materialized to a task grid by their export scripts; where this occurs, the manifest path, artifact metadata, and filename record the task-specific export, commonly with `_mean` or `taskgrid`.

For download size only, native AETHER rows and native AlphaEarth land-use rows are materialized once with this runtime policy and stored as `sample_id`-keyed entity tables. These tables contain the exact float values before row-wise L2 normalization; they do not change pooling, interpolation, splits, labels, or the downstream head. Their per-task alignment reports are included in the model ZIPs. The release manifest selects these tables directly, so users do not need the hundreds of GiB of unused city-wide pixels.

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
