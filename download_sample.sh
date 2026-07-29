#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

DATASET="${CITYREP_DATASET:-cityrep/cityrep/13}"
DEST="${CITYREP_SAMPLE_ROOT:-sample}"
REMOTE_FILE="cityrep_sample/singapore_alphaearth_pm25_mean__6b89dbc081.tif"
FILE_NAME="${REMOTE_FILE##*/}"

if ! command -v kaggle >/dev/null 2>&1; then
  cat >&2 <<'EOF'
The Kaggle CLI is required:

  pip install kaggle
  kaggle auth login
EOF
  exit 1
fi

mkdir -p "${DEST}"

echo "[sample] downloading ${REMOTE_FILE}"
kaggle datasets download \
  -d "${DATASET}" \
  -f "${REMOTE_FILE}" \
  -p "${DEST}" \
  -o

python scripts/inspect_embedding_sample.py \
  --input "${DEST}/${FILE_NAME}" \
  --metadata metadata/sample_embedding.json
