#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/python -m pip install -r requirements.txt

echo "Starting Streamlit dashboard..."
.venv/bin/python -m streamlit run streamlit_app.py
