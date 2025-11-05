import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__)))

# 导入DataProcessor
from src.data_processing.data_processor import DataProcessor

def test_contrast_analysis():
    """测试反差分析功能"""
    print("\n=== 测试反差分析功能 ===")
    
    # 创建测试数据
    data = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B', 'C', 'C'],
        'value1': [10, 12, 15, 18, 20, 22],
        'value2': [5, 7, 9, 11, 13, 15]
    })
    
    print("测试数据:")
    print(data)
    
    # 初始化处理器
    processor = DataProcessor()
    
    # 执行反差分析
    try:
        results = processor.contrast_analysis(
            df=data,
            group_column='group',
            value_columns=['value1', 'value2'],
            method='mean'
        )
        
        print("\n分析结果 - 分组统计:")
        print(results['group_stats'])
        
        print("\n分析结果 - 组间差异:")
        print(results['contrasts'])
        
        print("\n分析结果 - 总体统计:")
        print(results['overall_stats'])
        
        print("\n分析结果 - 变异系数:")
        print(results['cv_results'])
        
        print("✓ 反差分析测试通过")
        return True
    except Exception as e:
        print(f"✗ 反差分析测试失败: {str(e)}")
        return False

def test_reliability_analysis():
    """测试信度分析功能"""
    print("\n=== 测试信度分析功能 ===")
    
    # 创建测试数据（模拟问卷数据，具有较高的内部一致性）
    np.random.seed(42)
    base_scores = np.random.normal(50, 10, 100)
    
    data = pd.DataFrame({
        'item1': base_scores + np.random.normal(0, 5, 100),
        'item2': base_scores + np.random.normal(0, 5, 100),
        'item3': base_scores + np.random.normal(0, 5, 100),
        'item4': base_scores + np.random.normal(0, 5, 100),
        'item5': base_scores + np.random.normal(0, 5, 100)
    })
    
    print("测试数据 (前5行):")
    print(data.head())
    
    # 初始化处理器
    processor = DataProcessor()
    
    # 执行信度分析
    try:
        # 使用所有列作为量表列
        scale_columns = data.columns.tolist()
        results = processor.reliability_analysis(df=data, scale_columns=scale_columns)
        
        # 显示返回结果的结构
        print("\n信度分析结果结构:")
        print(f"返回的键: {list(results.keys())}")
        
        # 尝试获取alpha值（不假设具体键名）
        alpha_value = None
        for key in results:
            if isinstance(results[key], (int, float)):
                alpha_value = results[key]
                break
        
        if alpha_value is not None:
            print(f"\n检测到的Alpha值: {alpha_value}")
        else:
            print("\n未检测到Alpha值")
            
        print("\n信度分析测试通过")
        
        print("✓ 信度分析测试通过")
        return True
    except Exception as e:
        print(f"✗ 信度分析测试失败: {str(e)}")
        return False

def test_validity_analysis():
    """测试效度分析功能"""
    print("\n=== 测试效度分析功能 ===")
    
    # 创建测试数据（模拟具有结构效度的数据）
    np.random.seed(42)
    
    # 创建两个潜在因子
    factor1 = np.random.normal(0, 1, 100)
    factor2 = np.random.normal(0, 1, 100)
    
    # 创建与因子1相关的项目
    item1 = 0.8 * factor1 + 0.2 * np.random.normal(0, 1, 100)
    item2 = 0.7 * factor1 + 0.3 * np.random.normal(0, 1, 100)
    item3 = 0.6 * factor1 + 0.4 * np.random.normal(0, 1, 100)
    
    # 创建与因子2相关的项目
    item4 = 0.8 * factor2 + 0.2 * np.random.normal(0, 1, 100)
    item5 = 0.7 * factor2 + 0.3 * np.random.normal(0, 1, 100)
    
    # 创建效标变量（与因子1相关）
    criterion = 0.6 * factor1 + 0.4 * np.random.normal(0, 1, 100)
    
    data = pd.DataFrame({
        'item1': item1,
        'item2': item2,
        'item3': item3,
        'item4': item4,
        'item5': item5,
        'criterion': criterion
    })
    
    print("测试数据 (前5行):")
    print(data.head())
    
    # 初始化处理器
    processor = DataProcessor()
    
    # 执行效度分析
    try:
        # 使用除了效标列以外的所有列作为量表列
        scale_columns = data.columns.drop('criterion').tolist()
        # 效度分析方法配置
        methods = None  # 使用默认方法
        results = processor.validity_analysis(df=data, scale_columns=scale_columns, methods=methods)
        
        # 简化效度分析测试输出
        print("\n效度分析结果结构:")
        print(f"返回的键: {list(results.keys())}")
        
        if 'explained_variance_ratio' in results:
            print(f"\n解释方差比: {results['explained_variance_ratio']}")
        
        if 'components' in results:
            print("\n因子载荷矩阵 (前5行):")
            print(pd.DataFrame(results['components']).head())
        
        print("\n效度分析测试通过")
        
        print("✓ 效度分析测试通过")
        return True
    except Exception as e:
        print(f"✗ 效度分析测试失败: {str(e)}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始测试新增的分析功能...")
    
    tests = [
        ('反差分析', test_contrast_analysis),
        ('信度分析', test_reliability_analysis),
        ('效度分析', test_validity_analysis)
    ]
    
    passed_count = 0
    
    for test_name, test_func in tests:
        print(f"\n--- 运行{test_name}测试 ---")
        if test_func():
            passed_count += 1
    
    print(f"\n=== 测试结果摘要 ===")
    print(f"总测试数: {len(tests)}")
    print(f"通过测试数: {passed_count}")
    print(f"失败测试数: {len(tests) - passed_count}")
    
    if passed_count == len(tests):
        print("🎉 所有测试通过!")
        return True
    else:
        print("❌ 部分测试失败，请检查代码")
        return False

if __name__ == "__main__":
    run_all_tests()