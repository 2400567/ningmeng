@echo off
cls

echo ===================================================
echo         📊  AI数据分析系统 - 启动脚本  📊
echo ===================================================
echo 

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python。请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ 检测到Python环境
echo 

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 📦 创建Python虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo 📈 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📦 安装项目依赖...
pip install -r requirements.txt
pip install streamlit scikit-learn matplotlib openpyxl python-docx

REM 检查安装是否成功
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo 
echo ✅ 所有依赖安装完成！
echo ===================================================
echo 🌐 正在启动AI数据分析系统界面...
echo ===================================================
echo 
echo 💡 提示：
echo  - 系统将在浏览器中打开
necho  - 如有问题，请检查终端输出
necho  - 按Ctrl+C可以关闭服务
necho 

REM 启动Streamlit应用
streamlit run src\ui\app.py

REM 如果Streamlit启动失败，尝试通过main.py启动
if %errorlevel% neq 0 (
    echo 
echo ⚠️ Streamlit启动失败，尝试通过命令行模式启动...
    python main.py
)

pause