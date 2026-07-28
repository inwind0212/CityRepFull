# Ethics and Limitations

CityRep is built from processed spatial aggregates and public or
license-compatible data products. It does not redistribute raw street-view
images, raw POI dumps, or person-level records.

## Responsible Use

The benchmark is designed for scientific comparison of urban representation
models. It should not be used as a direct decision system for resource
allocation, policing, housing eligibility, individual profiling, or other
high-stakes decisions.

## Geographic Coverage

The release covers 8 cities. This scope is not representative of all
global urban conditions. Performance claims should be limited to the benchmark
configuration unless additional cities are registered and evaluated.

## Label Uncertainty

Several tasks rely on remote-sensing or modeled gridded products. Those labels
carry spatial smoothing, sensor, temporal, and modeling uncertainty from their
source datasets.

## Societal Bias

Street-view, POI, and remote-sensing model inputs can encode uneven coverage
across cities and neighborhoods. The framework exposes coverage diagnostics, but
benchmark scores should not be interpreted as unbiased measurements of urban
quality or social outcomes.

## AGE Task Caveat

Reference age-distribution aggregates exclude Mumbai, Nairobi, Jakarta, and
Cape Town because of source-data quality concerns. The corresponding task files
are retained for transparency.

