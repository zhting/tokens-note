@echo off
chcp 65001 >nul 2>&1
setlocal

set "PORT=8080"
set "ROOT=%~dp0"

echo ============================================
echo   雪糕 · AI 额度与订阅提醒  -  本地启动器
echo ============================================
echo.

REM 检查端口是否被占用，若占用则递增查找一个可用端口
set "FOUND_PORT="
for /L %%P in (%PORT%,1,8200) do (
    netstat -ano 2>nul | findstr /r /c:":%%P " >nul
    if errorlevel 1 (
        set "FOUND_PORT=%%P"
        goto :start
    )
)
if not defined FOUND_PORT (
    echo 无法在 %PORT%-8200 范围内找到可用端口，请手动关闭占用端口的程序。
    pause
    exit /b 1
)

:start
echo 使用端口: %FOUND_PORT%
echo 启动本地服务器: %ROOT%
echo.

REM 切换到项目根目录（server.py 以此为工作目录）
cd /d "%ROOT%"

REM 启动本地服务器（支持读写 ai-tools-data.json，最小化后台窗口运行）
start "" /min python server.py %FOUND_PORT%

REM 等待服务器就绪
ping -n 2 127.0.0.1 >nul

REM 打开浏览器窗口
start "" "http://127.0.0.1:%FOUND_PORT%/index.html"

echo 应用已在浏览器中打开。
echo 关闭此窗口不会停止服务器，如需停止请关闭后台 python 进程。
echo.
pause
endlocal
