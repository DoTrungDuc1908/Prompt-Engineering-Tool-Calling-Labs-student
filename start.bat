@echo off
chcp 65001 >nul
title 🕵️‍♂️ Research Agent Launcher with Cloudflare Tunnel

:: Color Definitions (ANSI escape codes)
set "ESC="
for /F %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
set "COLOR_BLUE=%ESC%[38;5;39m"
set "COLOR_GREEN=%ESC%[38;5;82m"
set "COLOR_YELLOW=%ESC%[38;5;220m"
set "COLOR_CYAN=%ESC%[38;5;51m"
set "COLOR_PURPLE=%ESC%[38;5;135m"
set "COLOR_RED=%ESC%[38;5;196m"
set "COLOR_RESET=%ESC%[0m"
set "COLOR_BOLD=%ESC%[1m"
set "COLOR_GRAY=%ESC%[90m"

cls
echo %COLOR_BLUE%========================================================================%COLOR_RESET%
echo   %COLOR_BOLD%%COLOR_CYAN%🕵️‍♂️  WELCOME TO RESEARCH AGENT LAUNCHER WITH CLOUDFLARE TUNNEL%COLOR_RESET%
echo %COLOR_BLUE%========================================================================%COLOR_RESET%
echo.

:: Check environment
if not exist "%~dp0starter_v0" (
    echo %COLOR_RED%[Error] Directory 'starter_v0' not found in %~dp0%COLOR_RESET%
    pause
    exit /b
)

:: Copy env if missing
if not exist "%~dp0starter_v0\.env" (
    if exist "%~dp0starter_v0\.env.example" (
        echo %COLOR_YELLOW%[Info] .env file not found. Copying .env.example...%COLOR_RESET%
        copy "%~dp0starter_v0\.env.example" "%~dp0starter_v0\.env" >nul
        echo %COLOR_GREEN%[Success] Created starter_v0\.env! Please open it to enter your API keys if needed.%COLOR_RESET%
    )
)

:: Locate cloudflared.exe
set "CLOUDFLARED_PATH="
if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
    set "CLOUDFLARED_PATH=C:\Program Files (x86)\cloudflared\cloudflared.exe"
) else if exist "C:\Program Files\cloudflared\cloudflared.exe" (
    set "CLOUDFLARED_PATH=C:\Program Files\cloudflared\cloudflared.exe"
) else (
    where cloudflared.exe >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "CLOUDFLARED_PATH=cloudflared"
    )
)

if "%CLOUDFLARED_PATH%"=="" (
    echo %COLOR_RED%[Warning] cloudflared.exe was not found in PATH or standard installation folders.%COLOR_RESET%
    echo %COLOR_YELLOW%We will try running 'cloudflared' globally, but it may fail.%COLOR_RESET%
    set "CLOUDFLARED_PATH=cloudflared"
)

:: Display Selection Menu
echo %COLOR_BOLD%Choose which interface you want to start and expose:%COLOR_RESET%
echo.
echo   %COLOR_CYAN%[1]%COLOR_RESET% %COLOR_BOLD%Streamlit Web UI%COLOR_RESET% (Port %COLOR_GREEN%8501%COLOR_RESET%) %COLOR_GRAY%- Highly recommended interactive dashboard%COLOR_RESET%
echo   %COLOR_CYAN%[2]%COLOR_RESET% %COLOR_BOLD%FastAPI Backend%COLOR_RESET% (Port %COLOR_GREEN%8000%COLOR_RESET%) %COLOR_GRAY%- API Server + Static HTML%COLOR_RESET%
echo   %COLOR_CYAN%[3]%COLOR_RESET% %COLOR_BOLD%Both Interfaces%COLOR_RESET% %COLOR_GRAY%- Starts both; Exposes Streamlit Web UI (8501)%COLOR_RESET%
echo.
set /p "UI_CHOICE=Enter your choice (1, 2, or 3) [Default: 1]: "

if "%UI_CHOICE%"=="" set "UI_CHOICE=1"

cd /d "%~dp0starter_v0"

if "%UI_CHOICE%"=="1" (
    echo.
    echo %COLOR_CYAN%[1/2] Starting Streamlit Web UI (port 8501)...%COLOR_RESET%
    start "RA-Streamlit-UI" cmd /c "title Streamlit UI Server && python -m streamlit run app.py --server.port 8501"
    
    echo %COLOR_GRAY%Waiting 5 seconds for Streamlit server to initialize...%COLOR_RESET%
    timeout /t 5 /nobreak >nul
    
    echo.
    echo %COLOR_CYAN%[2/2] Launching Cloudflare Tunnel to expose Streamlit...%COLOR_RESET%
    echo %COLOR_GRAY%------------------------------------------------------------------------%COLOR_RESET%
    echo   Local URL:    %COLOR_BOLD%%COLOR_BLUE%http://localhost:8501%COLOR_RESET%
    echo   %COLOR_YELLOW%Look for a URL ending in '.trycloudflare.com' in the console output!%COLOR_RESET%
    echo   %COLOR_GRAY%Copy the .trycloudflare.com link and paste it into REPORT.md or share it!%COLOR_RESET%
    echo   %COLOR_GRAY%Press Ctrl+C in this window to stop the tunnel.%COLOR_RESET%
    echo %COLOR_GRAY%------------------------------------------------------------------------%COLOR_RESET%
    echo.
    "%CLOUDFLARED_PATH%" tunnel --url http://localhost:8501
) else if "%UI_CHOICE%"=="2" (
    echo.
    echo %COLOR_CYAN%[1/2] Starting FastAPI Backend (port 8000)...%COLOR_RESET%
    start "RA-FastAPI-Server" cmd /c "title FastAPI Server && python -m uvicorn server:app --host 0.0.0.0 --port 8000 --no-reload"
    
    echo %COLOR_GRAY%Waiting 4 seconds for FastAPI server to initialize...%COLOR_RESET%
    timeout /t 4 /nobreak >nul
    
    echo.
    echo %COLOR_CYAN%[2/2] Launching Cloudflare Tunnel to expose FastAPI Backend...%COLOR_RESET%
    echo %COLOR_GRAY%------------------------------------------------------------------------%COLOR_RESET%
    echo   Local URL:    %COLOR_BOLD%%COLOR_BLUE%http://localhost:8000%COLOR_RESET%
    echo   %COLOR_YELLOW%Look for a URL ending in '.trycloudflare.com' in the console output!%COLOR_RESET%
    echo   %COLOR_GRAY%Copy the .trycloudflare.com link and paste it into REPORT.md or share it!%COLOR_RESET%
    echo   %COLOR_GRAY%Press Ctrl+C in this window to stop the tunnel.%COLOR_RESET%
    echo %COLOR_GRAY%------------------------------------------------------------------------%COLOR_RESET%
    echo.
    "%CLOUDFLARED_PATH%" tunnel --url http://localhost:8000
) else if "%UI_CHOICE%"=="3" (
    echo.
    echo %COLOR_CYAN%[1/3] Starting FastAPI Backend (port 8000)...%COLOR_RESET%
    start "RA-FastAPI-Server" cmd /c "title FastAPI Server && python -m uvicorn server:app --host 0.0.0.0 --port 8000 --no-reload"
    
    echo %COLOR_CYAN%[2/3] Starting Streamlit Web UI (port 8501)...%COLOR_RESET%
    start "RA-Streamlit-UI" cmd /c "title Streamlit UI Server && python -m streamlit run app.py --server.port 8501"
    
    echo %COLOR_GRAY%Waiting 5 seconds for servers to initialize...%COLOR_RESET%
    timeout /t 5 /nobreak >nul
    
    echo.
    echo %COLOR_CYAN%[3/3] Launching Cloudflare Tunnel (Tunneling Streamlit UI on 8501)...%COLOR_RESET%
    echo %COLOR_GRAY%------------------------------------------------------------------------%COLOR_RESET%
    echo   Local Streamlit UI:  %COLOR_BOLD%%COLOR_BLUE%http://localhost:8501%COLOR_RESET%
    echo   Local FastAPI API:   %COLOR_BOLD%%COLOR_BLUE%http://localhost:8000%COLOR_RESET%
    echo   %COLOR_YELLOW%Look for a URL ending in '.trycloudflare.com' in the console output!%COLOR_RESET%
    echo   %COLOR_GRAY%Copy the .trycloudflare.com link and paste it into REPORT.md or share it!%COLOR_RESET%
    echo   %COLOR_GRAY%Press Ctrl+C in this window to stop the tunnel.%COLOR_RESET%
    echo %COLOR_GRAY%------------------------------------------------------------------------%COLOR_RESET%
    echo.
    "%CLOUDFLARED_PATH%" tunnel --url http://localhost:8501
) else (
    echo %COLOR_RED%Invalid choice. Exiting...%COLOR_RESET%
)

pause
