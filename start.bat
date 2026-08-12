@echo off
chcp 65001 >nul 2>&1
setlocal

set "PORT=8080"
set "ROOT=%~dp0"

echo ============================================
echo   Local Launcher
echo ============================================
echo.

REM Check port availability
set "FOUND_PORT="
for /L %%P in (%PORT%,1,8200) do (
    netstat -ano 2>nul | findstr /r /c:":%%P " >nul
    if errorlevel 1 (
        set "FOUND_PORT=%%P"
        goto :start
    )
)
if not defined FOUND_PORT (
    echo No available port found.
    pause
    exit /b 1
)

:start
echo Port: %FOUND_PORT%
cd /d "%ROOT%"

REM Open browser
start "" "http://127.0.0.1:%FOUND_PORT%/index.html"

REM Start server in foreground
echo Server started, press Ctrl+C to stop.
python -u server.py %FOUND_PORT%

echo.
echo Server stopped.
pause
endlocal
