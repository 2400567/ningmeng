"""
AI数据分析大模型系统 - 主入口

该系统提供完整的数据分析流程：
1. 文件导入 - 支持多种数据格式
2. 智能模型选择 - 根据数据特征推荐合适的分析模型
3. 数据分析 - 数据清洗、特征提取和统计分析
4. 数据可视化 - 生成各类图表
5. 报告生成 - 导出专业的Word数据分析报告
6. AI智能体 - 辅助数据分析和报告撰写
"""

import os
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """检查运行环境"""
    logger.info("开始检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version
    logger.info(f"Python版本: {python_version}")
    
    # 检查必要的依赖
    required_packages = ['pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            version = __import__(package).__version__
            logger.info(f"{package}版本: {version}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"缺少依赖: {package}")
    
    # 检查streamlit是否可用
    streamlit_available = False
    try:
        import streamlit
        streamlit_available = True
        logger.info(f"streamlit版本: {streamlit.__version__}")
    except ImportError:
        logger.warning("streamlit不可用，Web界面将无法启动")
    
    if missing_packages:
        return False, missing_packages, streamlit_available
    else:
        logger.info("环境检查通过!")
        return True, [], streamlit_available

def run_command_line_mode():
    """命令行模式运行，提供核心功能"""
    print("\n===========================================================")
    print("=  📊  AI数据分析系统 - 命令行模式  📊")
    print("===========================================================")
    print("= 注意: Web界面依赖streamlit不可用，但核心功能仍然可以使用 =")
    print("===========================================================")
    
    # 尝试导入核心模块
    try:
        from src.data_processing.data_loader import DataLoader
        from src.data_processing.data_processor import DataProcessor
        
        print("\n✅ 核心模块导入成功!")
        print("\n可用功能:")
        print("1. 数据加载 (DataLoader)")
        print("2. 数据处理 (DataProcessor)")
        
        # 提供一个简单的示例
        print("\n📝 示例用法:")
        print("您可以通过Python代码使用以下功能:")
        print("\n# 导入数据")
        print("from src.data_processing.data_loader import DataLoader")
        print("loader = DataLoader()")
        print("data = loader.load_data('example_data.csv')")
        print("print(data.head())")
        
        # 运行一个简单的测试
        print("\n🔍 运行简单数据测试...")
        if os.path.exists('example_data.csv'):
            loader = DataLoader()
            data = loader.load_data('example_data.csv')
            print(f"✅ 成功加载示例数据: {data.shape[0]}行, {data.shape[1]}列")
            print("\n数据预览:")
            print(data.head())
        else:
            print("❌ 未找到example_data.csv文件")
            
    except Exception as e:
        print(f"\n❌ 核心模块导入失败: {e}")
        print("请确保已正确安装所有依赖。")

def main():
    """主函数"""
    logger.info("启动AI数据分析系统...")
    
    # 检查环境
    env_ok, missing_packages, streamlit_available = check_environment()
    
    # 显示欢迎信息
    print("\n===========================================================")
    print("=        📊  AI智能数据分析大模型系统  📊        =")
    print("===========================================================")
    print("= 功能: 导入数据 → 智能分析 → 生成可视化 → 导出报告 =")
    print("===========================================================")
    
    # 如果缺少核心依赖
    if not env_ok:
        logger.error(f"缺少必要依赖: {', '.join(missing_packages)}")
        print(f"\n❌ 错误: 缺少必要依赖: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖:")
        print(f"pip install {' '.join(missing_packages)}")
        return
    
    # 如果streamlit可用，尝试启动Web界面
    if streamlit_available:
        try:
            logger.info("尝试启动Web界面...")
            # 使用subprocess运行streamlit，这样可以更好地处理环境问题
            import subprocess
            streamlit_cmd = [sys.executable, '-m', 'streamlit', 'run', '/workspaces/ningmeng/AI/src/ui/app.py']
            logger.info(f"运行命令: {' '.join(streamlit_cmd)}")
            print("\n🌐 正在启动Web界面，请稍候...")
            print("如果浏览器没有自动打开，请访问 http://localhost:8501")
            print("\n按Ctrl+C停止应用")
            subprocess.run(streamlit_cmd)
        except Exception as e:
            logger.error(f"Web界面启动失败: {e}")
            print(f"\n❌ Web界面启动失败: {e}")
            print("\n将切换到命令行模式...")
            run_command_line_mode()
    else:
        # 如果streamlit不可用，启动命令行模式
        run_command_line_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        logger.exception(f"系统运行异常: {e}")
        print(f"\n❌ 系统运行异常: {e}")
        print("请检查日志文件ai_analyzer.log获取详细信息")
    finally:
        print("\n感谢使用AI数据分析系统!")