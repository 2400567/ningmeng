#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统测试脚本
用于测试AI智能数据分析系统的主要功能模块
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 测试数据加载
def test_data_loading():
    """测试数据加载功能"""
    print("\n=== 测试数据加载功能 ===")
    try:
        # 尝试加载示例数据
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_data.csv")
        data = pd.read_csv(data_path)
        print(f"✓ 成功加载示例数据，形状: {data.shape}")
        print(f"  列名: {list(data.columns)}")
        print(f"  前5行数据:\n{data.head()}")
        return data
    except Exception as e:
        print(f"✗ 数据加载失败: {str(e)}")
        return None

# 测试数据处理模块
def test_data_processor(data):
    """测试数据处理模块"""
    print("\n=== 测试数据处理模块 ===")
    try:
        from src.data_processing.data_processor import create_data_processor
        
        # 创建数据处理器
        processor = create_data_processor()
        print("✓ 成功创建数据处理器")
        
        # 测试数据清洗功能
        cleaned_data = processor.clean_data(
            data.copy(),
            missing_method="用均值填充",
            outlier_method="不处理",
            remove_duplicates=True
        )
        print(f"✓ 成功执行数据清洗，清洗后形状: {cleaned_data.shape}")
        
        # 测试相关性计算
        numeric_cols = cleaned_data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            corr_matrix = processor.calculate_correlations(cleaned_data)
            print(f"✓ 成功计算相关性矩阵，形状: {corr_matrix.shape}")
            
            # 找出强相关的特征对
            strong_correlations = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_correlations.append((numeric_cols[i], numeric_cols[j], corr_val))
            
            if strong_correlations:
                print(f"  发现 {len(strong_correlations)} 对强相关特征:")
                for f1, f2, corr in strong_correlations[:3]:
                    print(f"    - {f1} 与 {f2}: {corr:.3f}")
            else:
                print("  未发现强相关特征")
        
        return cleaned_data
    except Exception as e:
        print(f"✗ 数据处理测试失败: {str(e)}")
        return None

# 测试模型选择模块
def test_model_selector(data):
    """测试模型选择模块"""
    print("\n=== 测试模型选择模块 ===")
    try:
        from src.model_selection.model_selector import create_model_selector
        
        # 创建模型选择器
        selector = create_model_selector()
        print("✓ 成功创建模型选择器")
        
        # 测试模型推荐
        if '销量' in data.columns:
            recommendations = selector.recommend_models(
                data,
                target_col="销量",
                analysis_type="回归分析",
                accuracy_importance=7,
                speed_importance=5
            )
            print(f"✓ 成功生成模型推荐，推荐了 {len(recommendations)} 个模型")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec['model_name']} (评分: {rec['score']}/10)")
        else:
            print("✓ 跳过模型推荐测试：数据中没有'销量'列")
    except Exception as e:
        print(f"✗ 模型选择测试失败: {str(e)}")

# 测试可视化模块
def test_visualization(data):
    """测试可视化模块"""
    print("\n=== 测试可视化模块 ===")
    try:
        from src.visualization.visualizer import create_visualization_manager
        
        # 创建可视化管理器
        vis_manager = create_visualization_manager()
        print("✓ 成功创建可视化管理器")
        
        # 测试图表推荐
        recommendations = vis_manager.recommend_charts(data)
        print(f"✓ 成功生成图表推荐，推荐了 {len(recommendations)} 种图表")
        for i, chart in enumerate(recommendations[:3], 1):
            print(f"  {i}. {chart['chart_type']} - {chart['reason']}")
        
        # 测试简单图表生成
        if '价格' in data.columns and '销量' in data.columns:
            fig = vis_manager.create_scatter_plot(
                data=data,
                x_col='价格',
                y_col='销量',
                title='价格与销量关系图'
            )
            print("✓ 成功创建散点图")
    except Exception as e:
        print(f"✗ 可视化测试失败: {str(e)}")

# 测试AI助手模块
def test_ai_assistant(data):
    """测试AI助手模块"""
    print("\n=== 测试AI助手模块 ===")
    try:
        from src.ai_agent.ai_assistant import create_ai_assistant
        
        # 创建AI助手
        ai_assistant = create_ai_assistant()
        print("✓ 成功创建AI助手")
        
        # 测试简单查询
        response = ai_assistant.generate_response(
            "请简要描述一下这个数据集",
            data=data
        )
        print("✓ 成功获取AI助手响应")
        print(f"  AI响应: {response[:100]}...")
    except Exception as e:
        print(f"✗ AI助手测试失败: {str(e)}")

# 主测试函数
def main():
    """运行所有测试"""
    print("=== AI智能数据分析系统功能测试 ===")
    
    # 测试数据加载
    data = test_data_loading()
    if data is None:
        print("测试失败：无法继续测试，数据加载失败")
        return
    
    # 测试数据处理
    cleaned_data = test_data_processor(data)
    
    # 测试模型选择
    test_model_selector(data)
    
    # 测试可视化
    test_visualization(data)
    
    # 测试AI助手
    test_ai_assistant(data)
    
    print("\n=== 测试完成 ===")
    print("请运行Streamlit应用进行完整的功能测试")
    print("命令: streamlit run src/ui/app.py")

if __name__ == "__main__":
    main()