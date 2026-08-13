@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Find available Python launcher: pythonw first, then py -3 -w, then python
set "PY="
where pythonw >nul 2>&1 && set "PY=pythonw"
if not defined PY (
    where py >nul 2>&1 && set "PY=py -3 -w"
)
if not defined PY (
    where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

REM Launch asynchronously so this console closes immediately
start "" %PY% "%~dp0widget.py"
