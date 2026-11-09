#!/usr/bin/env bash
# Render & Linux automated build script for VyaparMitra
set -o errexit

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Building React frontend..."
if [ -d "frontend" ]; then
  cd frontend
  npm install
  npm run build
  cd ..
fi

echo "Initializing SQLite operational database..."
python -c "from src.api.db import init_db; init_db()"

echo "Build complete and ready for deployment!"
