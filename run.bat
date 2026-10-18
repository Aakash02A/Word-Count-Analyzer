@echo off
setlocal EnableDelayedExpansion
title Word Intelligence - One Click Runner

REM =====================================================================
REM  Word Intelligence v0.4 - Single-Click Project Runner
REM  Double-click to build (first run) + start MySQL, backend, frontend.
REM  Opens http://localhost in the default browser once the API is healthy.
REM =====================================================================

REM Always operate from the folder that contains this .bat file
cd /d "%~dp0"

echo.
echo ============================================================
echo   Word Intelligence - starting project
echo   Working dir: %CD%
echo ============================================================
echo.

REM ---- 1. Verify Docker Desktop is installed and running --------------
where docker >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Docker CLI not found on PATH.
    echo         Install Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo [OK] Docker daemon is running.

REM ---- 2. Ensure .env exists (copy from template on first run) --------
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Created .env from .env.example. Edit it if you need custom settings.
    ) else (
        echo [WARN] No .env or .env.example found; Docker Compose defaults will be used.
    )
) else (
    echo [OK] .env already present.
)

REM ---- 3. Build (only if images missing) and start all services -------
echo.
echo ------------------------------------------------------------
echo Starting MySQL + backend + frontend via docker compose...
echo (First run may take several minutes while images build.)
echo ------------------------------------------------------------

docker compose ps -q backend frontend 2>nul | findstr /r "." >nul
if errorlevel 1 (
    echo [INFO] Services not built yet; running "docker compose up -d --build"...
    docker compose up -d --build
) else (
    echo [INFO] Images already exist; running "docker compose up -d"...
    docker compose up -d
)

if errorlevel 1 (
    echo.
    echo [ERROR] docker compose failed to start. See messages above.
    pause
    exit /b 1
)

REM ---- 4. Wait for backend /health to return 200 ----------------------
echo.
echo Waiting for backend health check (http://localhost:8000/health)...
set /a _tries=0
:healthloop
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 goto healthok
set /a _tries+=1
if !_tries! geq 60 (
    echo [WARN] Backend did not report healthy in 60s. Opening UI anyway; check 'docker compose logs -f backend'.
    goto openbrowser
)
timeout /t 2 /nobreak >nul
goto healthloop

:healthok
echo [OK] Backend is healthy.

REM ---- 5. Open the app in the default browser -------------------------
:openbrowser
echo.
echo ============================================================
echo   Word Intelligence is up.
echo     Frontend  : http://localhost
echo     API docs  : http://localhost/api/v1/docs
echo     Backend   : http://localhost:8000/api/v1/docs (direct)
echo     Health    : http://localhost:8000/health
echo.
echo   To stop     : run "stop.bat" (or: docker compose down)
echo   To view logs: docker compose logs -f
echo ============================================================
echo.
start "" http://localhost

REM ---- 6. Keep the window open so the user can read status -------------
echo Press any key to close this window (services keep running in the background)...
pause >nul
endlocal
