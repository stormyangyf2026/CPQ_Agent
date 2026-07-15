@echo off
chcp 65001 >nul
echo ========================================
echo   CPQ Agent - Windows 依赖安装
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    echo 下载: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

python --version
echo.

echo [1/2] 升级 pip...
python -m pip install --upgrade pip -q

echo [2/2] 安装依赖...
python -m pip install deepagents fastapi uvicorn pyyaml requests python-dotenv langchain-deepseek langchain-core

echo.
echo ========================================
echo   安装完成！请设置 API Key 后启动:
echo   set DEEPSEEK_API_KEY=sk-your-key
echo   双击 CPQ Agent.exe
echo ========================================
pause
