#!/usr/bin/env python3
"""
增强版AI数据分析系统启动脚本
整合所有新功能的主界面
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        ('streamlit', 'streamlit'),
        ('pandas', 'pandas'), 
        ('numpy', 'numpy'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('plotly', 'plotly'),
        ('scikit-learn', 'sklearn'),
        ('scipy', 'scipy'),
        ('requests', 'requests'),
        ('python-docx', 'docx'),
        ('PyPDF2', 'PyPDF2')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"⚠️ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("正在安装...")
        
        for package_name in missing_packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], 
                             check=True, capture_output=True)
                print(f"✅ {package_name} 安装成功")
            except subprocess.CalledProcessError:
                print(f"❌ {package_name} 安装失败")
        
        print("请重新运行程序")
        return False
    
    return True

def setup_environment():
    """设置环境"""
    # 设置工作目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 创建必要的目录
    directories = [
        'temp',
        'temp/figures',
        'temp/reports',
        'temp/saved_results',
        'temp/templates',
        'docs',
        'examples'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ 环境设置完成")

def main():
    """主函数"""
    print("🚀 启动增强版AI数据分析系统...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 设置环境
    setup_environment()
    
    # 启动应用
    app_path = "src/ui/enhanced_app.py"
    
    if not os.path.exists(app_path):
        print(f"❌ 找不到应用文件: {app_path}")
        return
    
    print("📊 正在启动增强版数据分析系统...")
    print("🌐 应用将在浏览器中打开: http://localhost:8501")
    print("🛑 按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 启动Streamlit应用
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', app_path,
            '--server.port=8501',
            '--server.address=localhost',
            '--browser.gatherUsageStats=false',
            '--server.headless=false'
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()