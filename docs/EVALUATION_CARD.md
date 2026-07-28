# Evaluation Card

## Evaluation target

CityRep measures the predictive utility of a frozen urban representation after aligning it to a downstream task's registered sample units. It does not train or fine-tune the representation encoder on CityRep labels.

## Tasks and primary metrics

- Land use: classification, macro F1.
- Age distribution: distribution prediction, KL divergence (lower is better).
- Road density, population, GDP, nighttime lights, PM2.5, and daytime LST: regression, R2.

## Released protocols

The reference spatial protocol is `block10_5seed_mlp1024`: a task-specific 10 x 10 spatial block partition with seeds `42, 24, 7, 0, 100`. Whole non-empty blocks are assigned to train, validation, and test. The diagnostic `random_5seed_mlp1024` uses the same seeds and ratios without spatial grouping. Both sets of fixed sample-ID partitions are published under `splits/`.

A task's five partitions are shared by all 11 models. Different tasks do not have identical sample IDs or block occupancy, so their partitions are necessarily different even when the seed is the same.

## Alignment and input normalization

The evaluator supports raster, region/H3, point/entity, and coordinate-derived embeddings. The exact registered source and alignment rule for every model-city-task row is stored in `baselines/registry/embedding_manifest.csv`. Aligned embedding vectors are L2-normalized row by row. There is no feature-wise z-standardization.

See `docs/ALIGNMENT_POLICY.md` for the distinction between pre-materialized task-grid artifacts and runtime alignment.

## Downstream head

The common MLP is exactly:

```text
Linear(input_dim, 1024) -> ReLU -> Linear(1024, output_dim)
```

It uses Adam, learning rate `1e-3`, weight decay `0`, batch size `512`, at most `100` epochs, and validation-loss early stopping with patience `10`. The output/loss is MSE for regression, cross entropy for classification, and KL divergence after `log_softmax` for distribution prediction.

This is a common hidden width, not a model-dimension-matched width. All models otherwise use the same task units, split IDs, seeds, optimizer settings, and stopping rule.

## Target normalization compatibility

For the reference results, each regression target is normalized when the complete registered task table is loaded. The registry selects `zscore`, `log1p_zscore`, or `none`. Thus the released behavior uses task-level statistics before the split rather than fitting target statistics on the training fold only. This is documented explicitly because changing it would produce a different result set.

## Reporting

For each model-task-city, metrics are averaged across the five seeds. The main table then reports the mean and population standard deviation across cities. `C-Std.` is geographic heterogeneity, not seed uncertainty.
