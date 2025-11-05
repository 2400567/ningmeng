import subprocess
import sys
import os

print("📊 AI数据分析系统启动器 📊")
print("===========================")

# 确保安装了streamlit
try:
    import streamlit
    print("✅ streamlit已安装")
except ImportError:
    print("❌ streamlit未安装，正在安装...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', 'streamlit'])

# 直接使用streamlit运行app.py
print("🌐 正在启动应用...")
print("===========================")
print("应用启动后，请在浏览器中访问显示的URL")
print("按Ctrl+C可以停止应用")
print("===========================")

# 获取app.py的绝对路径
app_path = os.path.join('src', 'ui', 'app.py')
subprocess.run([sys.executable, '-m', 'streamlit', 'run', app_path])