@echo off
cls

echo 📊 AI数据分析系统启动器 📊
echo ===========================

echo 🔧 使用虚拟环境安装必要依赖...
cd d:\AI
venv\Scripts\pip install streamlit pandas numpy matplotlib scikit-learn openpyxl python-docx

if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败，尝试使用系统Python...
    pip install --user streamlit pandas numpy matplotlib scikit-learn openpyxl python-docx
)

echo 
echo 🌐 正在启动应用...
echo ===========================

venv\Scripts\python -m streamlit run src\ui\app.py

pause