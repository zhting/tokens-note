@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting widget (debug mode)...
"C:\Users\zhaoting\AppData\Local\Programs\Python\Python312\python.exe" "%~dp0widget.py"
echo.
echo Exit code: %ERRORLEVEL%
pause
