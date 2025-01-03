#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up environment..."
export PYTHONPATH=/app:$PYTHONPATH
export PORT=${PORT:-10000}
export HOST=${HOST:-0.0.0.0}
export OPERATION_MODE=render
export IS_RENDER=true

echo "Running pre-deploy checks..."
python -c "import backend_rag_ia.api.main"

echo "Build completed successfully!"
