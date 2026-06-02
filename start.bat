@echo off
chcp 65001 >nul
title Research Agent

echo ============================================
echo        RESEARCH AGENT - LAUNCHER
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Starting backend server (port 8000)...
start "RA-Server" cmd /c "python -m uvicorn server:app --host 0.0.0.0 --port 8000 --no-reload > server.log 2>&1"
if errorlevel 1 (
    echo [!] Failed to start. Make sure Python and uvicorn are installed.
    pause
    exit /b
)

timeout /t 3 /nobreak >nul

echo [2/3] Verifying server...
python -c "import httpx; httpx.get('http://localhost:8000/api/config', timeout=5)" >nul 2>&1
if errorlevel 1 (
    echo [!] Server not ready yet. Retrying...
    timeout /t 5 /nobreak >nul
)

echo [3/3] Starting Cloudflare Tunnel (TryCloudflare)...
echo.
echo    Local:     http://localhost:8000
echo    Tunnel URL appears below - share it with anyone!
echo    Press Ctrl+C to stop.
echo.
echo ============================================
cloudflared tunnel --url http://localhost:8000

pause
