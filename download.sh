#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

DATASET="${CITYREP_DATASET:-cityrep/cityrep/13}"
DEST="${CITYREP_DOWNLOAD_ROOT:-.}"

if ! command -v kaggle >/dev/null 2>&1; then
  cat >&2 <<'EOF'
The Kaggle CLI is required:

  pip install kaggle
  kaggle auth login
EOF
  exit 1
fi

mkdir -p "${DEST}"
scratch="$(mktemp -d)"
trap 'rm -rf "${scratch}"' EXIT

echo "[download] ${DATASET}"
kaggle datasets download -d "${DATASET}" -p "${scratch}" --unzip -o

mkdir -p "${DEST}/data" "${DEST}/splits"
cp -a "${scratch}/cityrep_core/data/." "${DEST}/data/"
cp -a "${scratch}/cityrep_core/splits/block10_5seed_mlp1024/." \
  "${DEST}/splits/block10_5seed_mlp1024/"
cp -a "${scratch}/cityrep_core/splits/random_5seed_mlp1024/." \
  "${DEST}/splits/random_5seed_mlp1024/"

if [[ -d "${scratch}/embeddings" ]]; then
  while IFS= read -r -d '' model_dir; do
    if [[ -d "${model_dir}/baselines" ]]; then
      cp -a "${model_dir}/." "${DEST}/"
    fi
  done < <(find "${scratch}/embeddings" -mindepth 1 -maxdepth 1 -type d -print0)
fi

echo "[download] done"
