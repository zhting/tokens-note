@echo off
setlocal
cd /d "%~dp0"
echo Starting widget in console...

if exist "%UserProfile%\miniconda3\python.exe" (
    set "PYEXE=%UserProfile%\miniconda3\python.exe"
    goto :run
)
where py >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%I in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%I"
)
if defined PYEXE goto :run

echo ERROR: No Python found.
pause
exit /b 1

:run
echo Python: %PYEXE%
"%PYEXE%" "%~dp0widget.py"
echo.
echo Exit code: %ERRORLEVEL%
pause
endlocal
