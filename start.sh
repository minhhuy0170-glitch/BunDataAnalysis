#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-10000}"

python scripts/ensure_streamlit_assets.py

exec streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT}" \
  --server.headless true
