@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 原生桌面小窗（tkinter），无需浏览器与服务
echo 正在启动雪糕桌面小窗...
start "" pythonw widget.py

if errorlevel 1 (
    echo 启动失败，请确认已安装 Python（含 tkinter）。
    pause
)
