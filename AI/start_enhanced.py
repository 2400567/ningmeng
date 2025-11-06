#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI数据分析系统 - 增强版启动器
简化启动流程，自动检查依赖和配置
"""

import subprocess
import sys
import os
from pathlib import Path
import importlib.util

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        print(f"当前版本: {sys.version}")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly',
        'scikit-learn',
        'openai',
        'python-docx',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (未安装)")
    
    if missing_packages:
        print(f"\n⚠️  发现 {len(missing_packages)} 个缺失的依赖包")
        install = input("是否自动安装缺失的依赖？(y/n): ")
        
        if install.lower() == 'y':
            print("🔄 正在安装依赖...")
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"✅ 已安装 {package}")
                except subprocess.CalledProcessError:
                    print(f"❌ 安装 {package} 失败")
                    return False
        else:
            print("❌ 请手动安装依赖后再运行")
            return False
    
    return True

def check_files():
    """检查必要文件"""
    current_dir = Path(__file__).parent
    required_files = [
        'enhanced_app.py',
        'src/template_management/template_manager.py',
        'src/data_processing/variable_merger.py', 
        'src/ai_analysis/model_selector.py',
        'src/results_display/spssau_renderer.py',
        'src/report_generation/ai_report_generator.py',
        'src/literature/smart_literature.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} (文件缺失)")
    
    if missing_files:
        print(f"\n❌ 发现 {len(missing_files)} 个缺失文件，请检查文件完整性")
        return False
    
    return True

def create_directories():
    """创建必要目录"""
    current_dir = Path(__file__).parent
    directories = [
        'temp/figures',
        'temp/reports',
        'temp/exports',
        'data/templates',
        'data/uploads'
    ]
    
    for dir_path in directories:
        full_path = current_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {dir_path}")

def check_api_keys():
    """检查API密钥配置"""
    print("\n🔑 API密钥配置检查:")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("✅ OpenAI API密钥已配置")
    else:
        print("⚠️  OpenAI API密钥未配置")
        print("   请设置环境变量 OPENAI_API_KEY")
        print("   或在应用中手动输入")
    
    # 可以添加其他API密钥检查
    print("💡 提示: 可以在应用界面中手动配置API密钥")

def start_application():
    """启动应用"""
    current_dir = Path(__file__).parent
    app_file = current_dir / 'enhanced_app.py'
    
    print("\n🚀 启动AI数据分析系统...")
    print("📍 应用将在浏览器中打开")
    print("⏹️  按 Ctrl+C 停止应用")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            str(app_file),
            '--server.port=8501',
            '--server.headless=false',
            '--browser.gatherUsageStats=false'
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🤖 AI数据分析系统 - 增强版启动器")
    print("=" * 50)
    
    # 系统检查
    print("\n🔍 系统检查...")
    
    if not check_python_version():
        return
    
    if not check_dependencies():
        return
    
    if not check_files():
        return
    
    # 环境准备
    print("\n📁 环境准备...")
    create_directories()
    
    # API配置检查
    check_api_keys()
    
    print("\n✅ 所有检查通过！")
    
    # 启动确认
    start = input("\n是否立即启动应用？(y/n): ")
    if start.lower() == 'y':
        start_application()
    else:
        print("📋 手动启动命令:")
        print(f"   streamlit run enhanced_app.py")
        print("🌐 默认地址: http://localhost:8501")

if __name__ == "__main__":
    main()