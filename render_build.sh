#!/usr/bin/env bash
# Render & Linux automated build script for VyaparMitra
set -o errexit

export PYTHONPATH="."

echo "Installing Python dependencies with no-cache..."
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "Building React frontend..."
if [ -d "frontend" ]; then
  if command -v npm &> /dev/null; then
    cd frontend
    npm install
    npm run build
    cd ..
  else
    echo "Notice: npm is not installed in current environment; skipping frontend build."
  fi
fi

echo "Initializing SQLite operational database..."
python -c "from src.api.db import init_db; init_db()"

echo "Build complete and ready for deployment!"

