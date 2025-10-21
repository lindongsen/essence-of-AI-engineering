#!/bin/bash
set -e

MODEL_DIR="/opt/whisper"
mkdir -p "${MODEL_DIR}/cache"

uv run whisperlivekit-server \
  --model_cache_dir "${MODEL_DIR}/cache" --model tiny.en \
  --host 0.0.0.0 --port 8001

