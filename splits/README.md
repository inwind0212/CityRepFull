# Fixed Splits

The public release contains 126 JSON files across two protocols:

- `block10_5seed_mlp1024/`: task-specific spatial-block partitions.
- `random_5seed_mlp1024/`: task-specific random diagnostic partitions.

Each file contains folds for seeds `42, 24, 7, 0, 100` and stores stable `sample_id` values rather than row numbers. Demo-only entries are not evaluation tasks and therefore have no split files.

```bash
python scripts/generate_fixed_splits.py \
  --task-registry data/tasks.json \
  --protocol-registry configs/release/protocols.json \
  --out-root splits
```

For a fixed complete task and seed, all 11 models use the same partition.
