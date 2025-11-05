import subprocess
import sys
import os

print("启动AI数据分析系统...")

# 优先尝试使用main.py作为入口
if os.path.exists('main.py'):
    print("使用main.py启动应用...")
    subprocess.run([sys.executable, 'main.py'])
else:
    print("使用streamlit启动app.py...")
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'src/ui/app.py'])

print("按Enter键退出...")
input()