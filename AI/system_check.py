#!/usr/bin/env python3
"""
系统状态检查脚本
检查增强版AI数据分析系统的所有组件状态
"""

import sys
import os
import importlib
from pathlib import Path
import subprocess

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python版本符合要求")
        return True
    else:
        print("❌ Python版本过低，需要3.8+")
        return False

def check_dependencies():
    """检查依赖包"""
    dependencies = [
        ('streamlit', 'Streamlit Web框架'),
        ('pandas', '数据处理库'),
        ('numpy', '数值计算库'),
        ('matplotlib', '基础绘图库'),
        ('seaborn', '统计绘图库'),
        ('plotly', '交互式图表库'),
        ('scikit-learn', '机器学习库'),
        ('scipy', '科学计算库'),
        ('requests', 'HTTP请求库'),
        ('docx', 'Word文档处理'),
        ('PyPDF2', 'PDF文档处理')
    ]
    
    print("\n📦 检查依赖包:")
    missing = []
    
    for package, description in dependencies:
        try:
            # 特殊处理包名
            import_name = package
            if package == 'docx':
                import_name = 'python-docx'
            elif package == 'scikit-learn':
                import_name = 'sklearn'
            
            if package == 'docx':
                import docx
            elif package == 'PyPDF2':
                import PyPDF2
            else:
                importlib.import_module(import_name)
            
            print(f"  ✅ {package}: {description}")
        except ImportError:
            print(f"  ❌ {package}: {description} - 未安装")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️ 缺少依赖: {', '.join(missing)}")
        print("运行以下命令安装:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def check_file_structure():
    """检查文件结构"""
    required_files = [
        'src/ui/enhanced_app.py',
        'src/data_processing/spss_analyzer.py',
        'src/ai_agent/academic_engine.py',
        'src/ai_agent/literature_search.py',
        'src/report_generation/report_templates.py',
        'src/report_generation/template_uploader.py',
        'src/visualization/advanced_visualizer.py',
        'src/config.py',
        'launch_enhanced.py',
        'requirements_enhanced.txt'
    ]
    
    required_dirs = [
        'src',
        'src/ui',
        'src/data_processing',
        'src/ai_agent',
        'src/report_generation',
        'src/visualization',
        'temp',
        'temp/figures'
    ]
    
    print("\n📁 检查文件结构:")
    
    # 检查目录
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ 目录: {directory}")
        else:
            print(f"  ❌ 目录缺失: {directory}")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"  🔧 已创建目录: {directory}")
            except Exception as e:
                print(f"  ❌ 无法创建目录: {e}")
    
    # 检查文件
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ 文件: {file_path}")
        else:
            print(f"  ❌ 文件缺失: {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_imports():
    """检查模块导入"""
    print("\n🔧 检查核心模块导入:")
    
    modules_to_check = [
        ('src.data_processing.spss_analyzer', 'SPSS分析模块'),
        ('src.ai_agent.academic_engine', 'AI学术引擎'),
        ('src.ai_agent.literature_search', '文献检索模块'),
        ('src.report_generation.report_templates', '报告模板模块'),
        ('src.visualization.advanced_visualizer', '高级可视化模块'),
        ('src.config', '系统配置模块')
    ]
    
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    import_success = True
    for module_name, description in modules_to_check:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {description}: {module_name}")
        except ImportError as e:
            print(f"  ❌ {description}: {module_name} - {e}")
            import_success = False
        except Exception as e:
            print(f"  ⚠️ {description}: {module_name} - 其他错误: {e}")
    
    return import_success

def check_streamlit():
    """检查Streamlit状态"""
    print("\n🌐 检查Streamlit:")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'streamlit', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✅ Streamlit版本: {version}")
            return True
        else:
            print(f"  ❌ Streamlit检查失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ Streamlit检查超时")
        return False
    except Exception as e:
        print(f"  ❌ Streamlit检查错误: {e}")
        return False

def check_ai_config():
    """检查AI配置"""
    print("\n🤖 检查AI配置:")
    
    # 检查环境变量
    qwen_key = os.getenv('QWEN_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if qwen_key:
        print(f"  ✅ 通义千问API密钥: 已配置 (长度: {len(qwen_key)})")
    else:
        print("  ⚠️ 通义千问API密钥: 未配置")
    
    if openai_key:
        print(f"  ✅ OpenAI API密钥: 已配置 (长度: {len(openai_key)})")
    else:
        print("  ⚠️ OpenAI API密钥: 未配置")
    
    print("  💡 AI功能可以在没有API密钥的情况下以演示模式运行")
    
    return True

def generate_system_report():
    """生成系统报告"""
    print("\n" + "="*60)
    print("📊 AI数据分析系统 Enhanced - 系统状态报告")
    print("="*60)
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("文件结构", check_file_structure),
        ("模块导入", check_imports),
        ("Streamlit", check_streamlit),
        ("AI配置", check_ai_config)
    ]
    
    results = {}
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results[check_name] = False
    
    # 总结
    print("\n" + "="*60)
    print("📋 检查总结:")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {check_name}: {status}")
    
    print(f"\n📊 总体状态: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 系统状态良好，可以正常运行!")
        print("\n🚀 启动命令:")
        print("  python launch_enhanced.py")
    else:
        print("⚠️ 系统存在问题，请根据上述检查结果进行修复")
        
        if not results.get("依赖包", True):
            print("\n💡 安装依赖包:")
            print("  pip install -r requirements_enhanced.txt")
        
        if not results.get("文件结构", True):
            print("\n💡 请确保所有必要文件都存在")
    
    return passed == total

def main():
    """主函数"""
    print("🔍 开始系统状态检查...")
    
    try:
        return generate_system_report()
    except KeyboardInterrupt:
        print("\n\n⛔ 检查被用户中断")
        return False
    except Exception as e:
        print(f"\n\n❌ 系统检查出现错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)