@echo off
setlocal
title Word Intelligence - Stopper
cd /d "%~dp0"

echo ============================================================
echo   Stopping Word Intelligence services...
echo ============================================================

docker compose ps -q >nul 2>nul
if errorlevel 1 (
    echo [INFO] Nothing to stop (no running services found).
    pause
    exit /b 0
)

REM Use "down" (keeps MySQL volume) so history data survives restarts.
REM Run "docker compose down -v" manually if you want to wipe data.
docker compose down

echo.
echo [OK] Services stopped. MySQL data volume was preserved.
echo      To also delete the database: docker compose down -v
echo.
pause
endlocal
