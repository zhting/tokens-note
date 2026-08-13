@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PORT=8099
set URL=http://127.0.0.1:%PORT%/widget.html

REM 检查端口是否已被占用（可能主应用已在运行）
netstat -ano | findstr ":%PORT%" | findstr "LISTENING" >nul
if %errorlevel% == 0 (
    echo 服务已在端口 %PORT% 运行，直接打开小窗口...
    goto open
)

REM 后台启动服务（使用 pythonw 不显示命令行窗口）
echo 正在启动服务（端口 %PORT%）...
start /B "" pythonw server.py %PORT%

REM 等待服务可用（最多 10 秒）
set /a tries=0
:wait
set /a tries+=1
if %tries% gtr 10 goto fail
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri '%URL%' -Method HEAD -TimeoutSec 1 -UseBasicParsing).StatusCode } catch { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 goto wait

:open
REM 优先使用 Edge，回退到 Chrome，再回退到默认浏览器
where msedge >nul 2>&1
if %errorlevel% == 0 (
    start "" msedge --app=%URL% --window-size=380,720 --window-position=1520,40
    goto end
)
where chrome >nul 2>&1
if %errorlevel% == 0 (
    start "" chrome --app=%URL% --window-size=380,720 --window-position=1520,40
    goto end
)
start "" %URL%

goto end

:fail
echo 启动服务失败，请检查 server.py 是否能正常运行。
pause

:end
