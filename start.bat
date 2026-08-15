@echo off
setlocal
cd /d "%~dp0"

REM ASCII-only. UTF-8 Chinese breaks cmd.exe on GBK Windows.

set "PORT=8080"
set "PYEXE="

echo ============================================
echo   Local Launcher
echo ============================================
echo.

if exist "%UserProfile%\miniconda3\python.exe" (
    "%UserProfile%\miniconda3\python.exe" -c "import http.server" >nul 2>&1
    if not errorlevel 1 goto :use_conda
)
goto :try_ana

:use_conda
set "PYEXE=%UserProfile%\miniconda3\python.exe"
goto :find_port

:try_ana
if exist "%UserProfile%\anaconda3\python.exe" (
    "%UserProfile%\anaconda3\python.exe" -c "import http.server" >nul 2>&1
    if not errorlevel 1 goto :use_ana
)
goto :try_py

:use_ana
set "PYEXE=%UserProfile%\anaconda3\python.exe"
goto :find_port

:try_py
where py >nul 2>&1
if errorlevel 1 goto :try_path
for /f "delims=" %%I in ('py -3 -c "import sys,http.server; print(sys.executable)" 2^>nul') do set "PYEXE=%%I"
if defined PYEXE goto :find_port

:try_path
for /f "delims=" %%I in ('where python 2^>nul') do (
    "%%I" -c "import http.server" >nul 2>&1
    if not errorlevel 1 (
        set "PYEXE=%%I"
        goto :find_port
    )
)

echo ERROR: No usable Python found. Install Python 3 and add it to PATH.
pause
exit /b 1

:find_port
set "FOUND_PORT="
for /L %%P in (%PORT%,1,8200) do (
    netstat -ano 2>nul | findstr /r /c:":%%P " >nul
    if errorlevel 1 (
        set "FOUND_PORT=%%P"
        goto :run
    )
)
echo ERROR: No available port found.
pause
exit /b 1

:run
echo Port: %FOUND_PORT%
echo Python: %PYEXE%
start "" "http://127.0.0.1:%FOUND_PORT%/index.html"
echo Server started. Press Ctrl+C to stop.
"%PYEXE%" -u server.py %FOUND_PORT%
echo.
echo Server stopped.
pause
endlocal
exit /b 0
