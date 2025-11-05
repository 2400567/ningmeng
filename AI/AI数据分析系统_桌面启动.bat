@echo off

REM AI数据分析系统桌面启动脚本
REM 创建日期: 2025-11-05
REM 更新: 使用launch_app.py实现单独窗口启动

REM 设置工作目录为脚本所在目录
cd /d "%~dp0"

REM 显示欢迎信息
echo ============================================================
echo =        📊  AI智能数据分析大模型系统 桌面启动器  📊        =
echo ============================================================
echo = 正在启动系统，请稍候...                                  =
echo ============================================================
echo. 
echo 🔄 系统将在单独窗口中启动...
echo.

REM 检查Python是否可用
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.6或更高版本
    echo 请访问 https://www.python.org/downloads/ 下载并安装
    pause
    exit /b 1
)

REM 运行launch_app.py以实现单独窗口启动
python launch_app.py

REM 启动器窗口会自动关闭，应用在单独窗口中运行