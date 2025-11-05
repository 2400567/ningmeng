# 🚀 AI数据分析系统 - 快速启动指南

## 📁 样例文件与参考资料

### 🗂️ 核心文档
- **SAMPLE_DATA_GUIDE.md** - 详细的样例数据使用指南
- **ANALYSIS_EXAMPLES.md** - 8个完整的分析示例与结果解释
- **REFERENCES.md** - 25篇权威学术文献参考库
- **comprehensive_test_data.csv** - 500样本26变量综合测试数据集

### 📊 推荐学习路径
1. **新手用户**: 阅读SAMPLE_DATA_GUIDE.md → 尝试基础分析
2. **进阶用户**: 参考ANALYSIS_EXAMPLES.md → 学习结果解释
3. **专业用户**: 查阅REFERENCES.md → 深度理论学习

## 系统状态

✅ 系统核心功能已开发完成并通过基础测试
✅ 所有必要的模块和功能都已实现
✅ 包含示例数据文件供测试使用

## 启动系统的三种方法

### 方法1：使用批处理脚本（推荐）

1. 在Windows资源管理器中导航到 `d:\AI` 目录
2. 双击运行 `run_app.bat` 文件
3. 脚本会自动：
   - 创建Python虚拟环境
   - 安装所有必要依赖
   - 启动Streamlit界面

### 方法2：手动命令行启动

1. 打开命令提示符或PowerShell
2. 执行以下命令：

```cmd
cd d:\AI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install streamlit scikit-learn matplotlib openpyxl python-docx
streamlit run src/ui/app.py
```

### 方法3：基础功能测试

如果只需测试核心功能（不使用界面），可以运行：

```cmd
cd d:\AI
python minimal_test.py
```

## 系统文件说明

- **example_data.csv**: 示例数据集（30行9列产品数据）
- **src/**: 源代码目录，包含所有核心模块
- **minimal_test.py**: 基础功能测试脚本
- **run_app.bat**: 一键启动脚本
- **README.md** 和 **User_Guide.md**: 完整文档

## 已知问题与解决方案

1. **依赖安装失败**
   - 确保已安装Python 3.8或更高版本
   - 尝试使用管理员权限运行命令提示符

2. **Streamlit界面无法启动**
   - 检查依赖是否正确安装
   - 可以通过 `python main.py` 使用命令行模式

3. **中文显示问题**
   - 系统已配置支持中文显示
   - 如遇乱码，请确保系统字体支持中文

## 系统功能概述

- 📊 数据导入与清洗
- 🔍 智能数据分析与特征提取
- 📈 多种可视化图表生成
- 🤖 智能模型推荐与选择
- 📝 专业报告自动生成
- 💬 AI助手辅助分析

祝您使用愉快！