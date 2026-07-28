# Raw Data Sources And Task Rebuilding

The release package includes benchmark-ready task data under `data/tasks/`.
Sixty-three task payloads are the canonical public evaluation inputs. The
London land-use directory is a synthetic schema demo; reported London land-use
metrics come from a separate, non-redistributed reference task. This document
records raw-data provenance and the processing interface for rebuilding tasks
whose source terms permit local access and processing.

## Processing Interface

Use the public CLI to convert downloaded raw files into the standard benchmark
task layout. For a new city with multiple tasks, the user-facing command is
`extend-city`; for one-off task construction, `prepare-task` is also available.

```text
data/tasks/<task_id>/
  labels.tif        # raster/distribution/regression tasks when applicable
  samples.parquet   # point samples consumed by the evaluator
  task.json         # provenance and processing metadata
data/tasks.json     # task registry
```

Raster task example:

```bash
python -m urban_benchmark prepare-task \
  --city london \
  --task population \
  --year 2024 \
  --source-kind raster \
  --raw-path external_raw/worldpop/london/worldpop_2024.tif \
  --task-type regression \
  --source "WorldPop Population Counts, constrained, 100m, R2024B, 2024" \
  --license "CC BY 4.0" \
  --normalization zscore \
  --task-registry data/tasks.json
```

Distribution raster example:

```bash
python -m urban_benchmark prepare-task \
  --city london \
  --task age_distribution \
  --year 2024 \
  --source-kind raster \
  --raw-path external_raw/worldpop_age/london/age_distribution_2024_10bin.tif \
  --task-type distribution \
  --label-cols age_00_04,age_05_14,age_15_24,age_25_34,age_35_44,age_45_54,age_55_64,age_65_74,age_75_84,age_85_plus \
  --source "WorldPop age-sex counts aggregated to 10 age-bin distributions, 2024" \
  --license "CC BY 4.0" \
  --task-registry data/tasks.json
```

Open land-use/sample task example:

```bash
python -m urban_benchmark prepare-task \
  --city example_city \
  --task landuse \
  --year 2026 \
  --source-kind samples \
  --raw-path /path/to/open_landuse_points.parquet \
  --task-type classification \
  --label-col label \
  --label-id-col label_id \
  --source "Documented open land-use source" \
  --license "Exact source licence and URL" \
  --task-registry data/tasks.json
```

The released London land-use file is synthetic and is not a reconstruction input. The Verisk-derived reference task used for reported London metrics is intentionally not redistributed.

For multiple tasks in one city, use `extend-city` with a local CSV/JSON task
manifest:

```bash
python -m urban_benchmark extend-city \
  --city london \
  --boundary external_raw/boundaries/london.geojson \
  --task-manifest external_raw/london_task_manifest.csv \
  --task-registry data/tasks.json \
  --allow-download-commands
```

The CLI is intentionally source-agnostic. A task manifest row can point to an
already downloaded file through `raw_path`, or it can include a
`download_command` that creates `raw_path` before preprocessing. Download
commands are only executed when `--allow-download-commands` is passed. This
keeps API credentials, Earth Engine authentication, manually accepted licenses,
and large external downloads out of the benchmark core while still supporting a
one-command city extension workflow.

## Raw Source Inventory

| Task | Raw source | Year | License / access note | Expected downloaded form |
|---|---|---:|---|---|
| Population | WorldPop Population Counts, constrained, 100m, R2024B | 2024 | CC BY 4.0 | One clipped GeoTIFF per city under `external_raw/worldpop/<city>/worldpop_2024.tif` |
| GDP | Kummu et al. gridded GDP, Zenodo DOI `10.5281/zenodo.18429133` | 2024 band | CC BY 4.0 | One clipped GeoTIFF per city under `external_raw/gdp/<city>/gdp_total_2024_30arcsec.tif` |
| Nightlight | VIIRS VNL V2.2 annual nighttime lights, `average_masked` radiance | 2024 | Public domain | One clipped GeoTIFF per city under `external_raw/nighttime_lights/eog_vnl_v22/<city>/vnl_v22_2024_average_masked-cf_cvg.tif` |
| PM2.5 | SEDAC/CIESIN Global Annual PM2.5 Grids, V5.GL.04 | 2022 | CIESIN open data policy; cite DOI `10.7927/as2r-9p42` | One clipped GeoTIFF per city under `external_raw/pm25/<city>/pm25_2022.tif` |
| Age distribution | WorldPop age-sex counts aggregated to 10 age bins | 2024 | CC BY 4.0 | One 10-band distribution GeoTIFF per city under `external_raw/worldpop_age_distribution/<city>/age_distribution_2024_10bin.tif` |
| Land use | City/open zoning and land-use point sources, harmonized to 12 benchmark classes | 2026 processing snapshot | City-specific terms; verify before redistribution | Point table/vector file with `x`, `y`, and harmonized `label_id` or mappable source class/code |
| Road density | OpenStreetMap highway ways from Overpass | downloaded 2026-04-28 | ODbL 1.0; attribution required | One road-density GeoTIFF per city under `external_raw/road_density/<city>/road_density_2026.tif` |
| LST | MODIS/Terra MOD11A2.061 8-day daytime LST annual mean | 2024 | NASA/LP DAAC MODIS terms; cite DOI `10.5067/MODIS/MOD11A2.061` | One clipped GeoTIFF per city under `external_raw/modis_lst/<city>/lst_day_mean_2024.tif` |

## City Boundaries

If raw rasters are downloaded globally or over a larger region, pass a city
boundary with `--boundary path/to/city.geojson --clip`. The boundary is reprojected
to the raster CRS before clipping. If the raw raster is already clipped to the
benchmark city extent, omit `--clip` and the script copies it directly.

## Land-Use Harmonization

The release uses the harmonized 12-class land-use scheme:

```text
Residential, Mixed Use, Commercial, Industrial, Transportation,
Green / Recreation, Institutional / Civic, Utilities, Water,
Agriculture / Rural, Vacant / Reserve, Other
```

The mapping audit tables are exported under:

```text
results/mapping/landuse_mapping_table_readable.csv
results/mapping/audit_tables/
```

For a new city, create a mapping CSV from the source category/code to `label_id`
and pass it with:

```bash
--mapping-csv path/to/mapping.csv --mapping-source-col source_code --mapping-target-col label_id
```

## Reproducibility Contract

The downstream evaluator consumes `data/tasks.json` plus the task directories.
As long as the rebuilt files follow this schema, the same alignment, split, and
evaluation code can be used for the original 8 cities, new cities, or new tasks.
