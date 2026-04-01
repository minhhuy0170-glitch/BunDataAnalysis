#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-10000}"

exec streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT}" \
  --server.headless true
