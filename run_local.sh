#!/usr/bin/env bash
set -e

echo "Starting Q-Play Reinforcement Learning Platform..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

if [ ! -d "frontend/dist" ]; then
    echo "Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

echo "Starting Server on http://127.0.0.1:8000 ..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
