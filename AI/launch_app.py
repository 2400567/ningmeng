import subprocess
import sys
import os
import time

# 安装必要的依赖
def install_dependencies():
    print("正在检查并安装依赖项...")
    
    # 使用虚拟环境的pip或系统pip（兼容Windows和Unix）
    if os.name == 'nt':
        venv_pip = os.path.join('venv', 'Scripts', 'pip.exe')
        venv_python = os.path.join('venv', 'Scripts', 'python.exe')
    else:
        venv_pip = os.path.join('venv', 'bin', 'pip')
        venv_python = os.path.join('venv', 'bin', 'python')

    if os.path.exists(venv_pip):
        pip_cmd = venv_pip
        python_cmd = venv_python
        print(f"使用虚拟环境: {python_cmd}")
    else:
        # 使用当前解释器的 -m pip 来保证与当前 Python 一致
        pip_cmd = None
        python_cmd = sys.executable
        print(f"使用系统Python: {python_cmd}")
    
    packages = [
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'plotly',  # 添加plotly到依赖列表
        'streamlit',
        'scikit-learn'
    ]
    
    def install_with_pip(pip_path, packages_list, user_mode=False):
        success = True
        for package in packages_list:
            try:
                print(f"安装 {package}...")
                if pip_path:
                    cmd = [pip_path, 'install', '--upgrade']
                    if user_mode:
                        cmd.append('--user')
                    cmd.append(package)
                else:
                    # 使用当前 python -m pip 安装，跨平台且更可靠
                    cmd = [python_cmd, '-m', 'pip', 'install', '--upgrade']
                    if user_mode:
                        cmd.append('--user')
                    cmd.append(package)

                subprocess.check_call(cmd)
                print(f"✅ {package} 安装成功")
                time.sleep(1)
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败 (返回码 {e.returncode}): {e}")
                success = False
            except Exception as e:
                print(f"❌ {package} 安装异常: {e}")
                success = False
        return success
    
    # 先尝试正常安装
    if install_with_pip(pip_cmd, packages):
        return python_cmd

    # 如果失败，尝试使用--user参数
    print("尝试使用--user参数安装...")
    if install_with_pip(pip_cmd, packages, user_mode=True):
        return python_cmd

    # 最后再尝试使用当前解释器的 -m pip 强制安装
    print("尝试使用当前 Python 的 -m pip 安装...")
    if install_with_pip(None, packages, user_mode=True):
        return python_cmd

    print("❌ 无法安装必要的依赖!")
    return None

# 测试streamlit是否安装成功
def test_streamlit(python_cmd):
    try:
        print("测试streamlit安装...")
        result = subprocess.run([python_cmd, '-c', 'import streamlit; print(streamlit.__version__)'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ streamlit安装成功，版本: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ streamlit测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ streamlit测试异常: {e}")
        return False

# 启动应用
def start_app(python_cmd):
    if not python_cmd:
        print("❌ 无法安装必要的依赖，启动失败!")
        return False
    
    print("\n🌐 正在启动应用...")
    print("===========================")
    
    # 首先测试streamlit
    streamlit_available = test_streamlit(python_cmd)
    
    try:
        # 检查main.py是否存在，如果存在优先使用main.py作为入口
        if os.path.exists('main.py'):
            print("使用main.py作为应用入口...")
            print("在单独窗口中启动应用...")
            # 使用start命令在单独窗口中启动
            if os.name == 'nt':  # Windows系统
                # 在Windows中使用start命令在新窗口中启动
                subprocess.run(f'start cmd /k "{python_cmd} main.py"', shell=True)
            else:
                # 非Windows系统的备选方案
                subprocess.Popen([python_cmd, 'main.py'])
        else:
            # 如果没有main.py，直接使用streamlit
            if streamlit_available:
                print("使用streamlit直接运行app.py...")
                print("在单独窗口中启动应用...")
                if os.name == 'nt':  # Windows系统
                    subprocess.run(f'start cmd /k "{python_cmd} -m streamlit run src/ui/app.py"', shell=True)
                else:
                    subprocess.Popen([python_cmd, '-m', 'streamlit', 'run', 'src/ui/app.py'])
            else:
                print("❌ streamlit不可用，无法启动Web界面!")
        return True
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        return False

if __name__ == "__main__":
    # 设置工作目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python可执行文件: {sys.executable}")
    
    python_cmd = install_dependencies()
    start_app(python_cmd)
    
    print("\n应用已在单独窗口中启动!")
    print("按Enter键关闭此窗口...")
    input()