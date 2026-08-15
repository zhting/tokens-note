@echo off
setlocal
cd /d "%~dp0"

REM ASCII-only. UTF-8 Chinese breaks cmd.exe on GBK Windows.

if exist "%UserProfile%\miniconda3\python.exe" (
    "%UserProfile%\miniconda3\python.exe" -c "import json" >nul 2>&1
    if not errorlevel 1 goto :use_conda
)
goto :try_ana

:use_conda
set "PYEXE=%UserProfile%\miniconda3\python.exe"
goto :launch

:try_ana
if exist "%UserProfile%\anaconda3\python.exe" (
    "%UserProfile%\anaconda3\python.exe" -c "import json" >nul 2>&1
    if not errorlevel 1 goto :use_ana
)
goto :try_py

:use_ana
set "PYEXE=%UserProfile%\anaconda3\python.exe"
goto :launch

:try_py
set "PYEXE="
where py >nul 2>&1
if errorlevel 1 goto :try_path
for /f "delims=" %%I in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%I"
if defined PYEXE goto :launch

:try_path
for /f "delims=" %%I in ('where python 2^>nul') do (
    "%%I" -c "import json" >nul 2>&1
    if not errorlevel 1 (
        set "PYEXE=%%I"
        goto :launch
    )
)

echo.
echo ERROR: No usable Python found.
echo Install official Python 3, or use Miniconda:
echo   %UserProfile%\miniconda3\python.exe
echo.
pause
exit /b 1

:launch
set "PYW=%PYEXE%"
if /i "%PYEXE:~-10%"=="python.exe" set "PYW=%PYEXE:~0,-10%pythonw.exe"
if not exist "%PYW%" set "PYW=%PYEXE%"
start "" "%PYW%" "%~dp0fullview.py"
endlocal
exit /b 0
