# Released Embeddings

CityRep publishes frozen embedding outputs, not baseline pretraining or upstream model code.

- `registry/embedding_manifest.csv` is the canonical model–city–task index.
- `registry/models.json` summarizes the 11 released models.
- Kaggle stores the embedding bytes in 11 model-level ZIP archives.
- After `./download.sh embeddings`, archives extract to the relative `baselines/artifacts/` paths recorded in the manifest.

The manifest has 704 logical rows with task-specific availability metadata. Place2Vec is represented by H3 lookup embeddings; `PE` is the deterministic position-embedding baseline. The repository includes the common evaluator, alignment implementation, fixed-split generator, and exact downstream protocol, but not model-training pipelines or raw model inputs.
