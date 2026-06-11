@echo off

IF NOT EXIST node_modules (
    echo Installing dependencies...
    npm install
)

IF NOT EXIST .env (
    copy .env.example .env
    echo Created .env from .env.example
)

echo Starting frontend at http://localhost:5173 ...
npm run dev
