@echo off

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    venv\Scripts\pip install -r requirements.txt
)

IF NOT EXIST .env (
    copy .env.example .env
    echo Created .env from .env.example - fill in your GEMINI_API_KEY
)

IF NOT EXIST data mkdir data

echo Starting backend at http://localhost:8000 ...
venv\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
