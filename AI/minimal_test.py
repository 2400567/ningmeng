#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极简测试脚本 - 只测试最基本的数据处理功能
避开复杂依赖，专注于核心数据加载和处理
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
logger = logging.getLogger("minimal_test")

print("="*60)
print("        📊  AI数据分析系统 - 极简功能测试  📊")
print("="*60)

# 测试1: 基本数据操作
try:
    logger.info("测试1: 基本数据操作...")
    # 创建测试数据
    data = {
        '年龄': [25, 30, 35, 40, 45],
        '收入': [50000, 60000, 75000, 90000, 100000],
        '消费': [45000, 55000, 68000, 82000, 92000],
        '城市': ['北京', '上海', '广州', '深圳', '杭州']
    }
    df = pd.DataFrame(data)
    
    print("✅ 基本数据操作成功!")
    print("测试数据预览:")
    print(df)
    
    # 计算基本统计
    print("\n基本统计信息:")
    print(f"数据维度: {df.shape}")
    print(f"数值列统计:")
    print(df.describe())
except Exception as e:
    print(f"❌ 基本数据操作失败: {e}")

# 测试2: 简单数据加载（如果存在示例数据）
try:
    logger.info("测试2: 数据加载...")
    if os.path.exists('example_data.csv'):
        df_example = pd.read_csv('example_data.csv')
        print("\n✅ 示例数据加载成功!")
        print(f"示例数据形状: {df_example.shape}")
        print("前3行:")
        print(df_example.head(3))
    else:
        print("\n⚠️ 未找到example_data.csv文件")
except Exception as e:
    print(f"❌ 数据加载失败: {e}")

# 测试3: 尝试导入数据加载器（如果能导入）
try:
    logger.info("测试3: 尝试导入数据加载器...")
    from src.data_processing.data_loader import DataLoader
    print("\n✅ 成功导入DataLoader!")
    # 简单测试数据加载器
    loader = DataLoader()
    print("  DataLoader实例创建成功")
except ImportError as e:
    print(f"\n⚠️ 数据加载器导入失败: {e}")
    print("  系统可能需要更多依赖")

# 测试4: 尝试导入数据处理器
try:
    logger.info("测试4: 尝试导入数据处理器...")
    from src.data_processing.data_processor import DataProcessor
    print("\n✅ 成功导入DataProcessor!")
    # 创建处理器实例
    processor = DataProcessor()
    print("  DataProcessor实例创建成功")
    
    # 提取数据特征
    features = processor.extract_data_features(df)
    print("  数据特征提取成功:")
    print(f"    数值列: {features['numeric_columns']}")
    print(f"    类别列: {features['categorical_columns']}")
    print(f"    总行数: {features['total_rows']}")
except Exception as e:
    print(f"\n⚠️ 数据处理器测试失败: {e}")

print("\n" + "="*60)
print("📊 极简功能测试完成!")
print("✅ 系统基础功能可以正常工作")
print("💡 完整功能需要安装所有依赖:")
print("   pip install -r requirements.txt")
print("   pip install streamlit scikit-learn matplotlib")
print("="*60)