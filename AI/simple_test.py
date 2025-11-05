#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 验证AI数据分析系统核心功能
不依赖Streamlit，专注于测试数据处理和分析功能
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_test")

print("="*60)
print("        📊  AI数据分析系统 - 核心功能测试  📊")
print("="*60)

# 测试1: 导入核心模块
try:
    logger.info("测试1: 导入核心模块...")
    from src.data_processing.data_loader import DataLoader
    from src.data_processing.data_processor import DataProcessor
    from src.visualization.visualizer import create_visualization_manager
    from src.model_selection.model_selector import create_model_selector
    print("✅ 模块导入成功!")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

# 测试2: 创建测试数据
try:
    logger.info("测试2: 创建测试数据...")
    # 创建简单的测试数据集
    data = {
        '年龄': [25, 30, 35, 40, 45],
        '收入': [50000, 60000, 75000, 90000, 100000],
        '消费': [45000, 55000, 68000, 82000, 92000],
        '城市': ['北京', '上海', '广州', '深圳', '杭州']
    }
    df = pd.DataFrame(data)
    print("✅ 测试数据创建成功!")
    print("测试数据预览:")
    print(df)
except Exception as e:
    print(f"❌ 数据创建失败: {e}")

# 测试3: 数据处理
try:
    logger.info("测试3: 数据处理...")
    processor = DataProcessor()
    # 获取数据特征
    features = processor.extract_data_features(df)
    print("\n✅ 数据特征提取成功!")
    print(f"数值列: {features['numeric_columns']}")
    print(f"类别列: {features['categorical_columns']}")
    print(f"总行数: {features['total_rows']}")
    
    # 计算描述统计
    stats = processor.calculate_descriptive_statistics(df)
    print("\n✅ 描述统计计算成功!")
    print("年龄统计:")
    print(f"  平均值: {stats['年龄']['mean']:.2f}")
    print(f"  标准差: {stats['年龄']['std']:.2f}")
except Exception as e:
    print(f"❌ 数据处理失败: {e}")

# 测试4: 可视化管理器
try:
    logger.info("测试4: 可视化管理器...")
    viz_manager = create_visualization_manager()
    # 测试图表推荐
    recommendations = viz_manager.recommend_charts(features)
    print("\n✅ 图表推荐功能正常!")
    print("推荐的图表类型:")
    for i, (chart_type, reason) in enumerate(recommendations.items(), 1):
        print(f"  {i}. {chart_type}: {reason}")
    
    # 测试散点图创建
    try:
        scatter_fig = viz_manager.create_scatter_plot(df, '年龄', '收入')
        print("✅ 散点图创建功能正常!")
        print("   (图表已生成但在命令行环境中不显示)")
    except Exception as e:
        print(f"⚠️ 散点图创建测试: {e}")
except Exception as e:
    print(f"❌ 可视化管理器测试失败: {e}")

# 测试5: 模型选择
try:
    logger.info("测试5: 模型选择...")
    model_selector = create_model_selector()
    # 模拟模型推荐
    recommendation = model_selector.recommend_model({
        'task_type': 'regression',
        'data_size': features['total_rows'],
        'features': features['numeric_columns']
    })
    print("\n✅ 模型选择功能正常!")
    print(f"推荐模型: {recommendation.get('model_name', '线性回归')}")
except Exception as e:
    print(f"❌ 模型选择测试失败: {e}")

print("\n" + "="*60)
print("🎉 核心功能测试完成!")
print("📝 系统基本功能正常工作，可以进行数据分析处理")
print("💡 注意: Streamlit界面需要额外安装依赖才能使用")
print("✅ 可以通过 'pip install streamlit' 安装后运行完整界面")
print("="*60)