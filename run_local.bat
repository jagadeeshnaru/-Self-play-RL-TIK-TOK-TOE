@echo off
echo ========================================================
echo Starting Q-Play Reinforcement Learning Platform...
echo ========================================================

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

if not exist "frontend\dist" (
    echo Building frontend...
    cd frontend
    npm install
    npm run build
    cd ..
)

echo Starting Server on http://127.0.0.1:8000 ...
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
