#!/usr/bin/env python3
"""
测试数据加载功能
"""

import sys
import os
import pandas as pd
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.data_processing.data_loader import DataLoader, DataValidator
    print("✅ 成功导入 DataLoader 和 DataValidator")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def create_test_data():
    """创建测试数据"""
    # 创建示例数据
    data = {
        '产品ID': [f'P{i:04d}' for i in range(1, 101)],
        '产品类别': ['电子产品', '服装', '家居', '食品', '图书'] * 20,
        '销售额': [1000 + i * 50 for i in range(100)],
        '销售量': [10 + i for i in range(100)],
        '客户年龄': [25 + (i % 40) for i in range(100)],
        '客户性别': ['男', '女'] * 50,
        '地区': ['北京', '上海', '广州', '深圳', '杭州'] * 20,
    }
    
    df = pd.DataFrame(data)
    
    # 确保temp目录存在
    os.makedirs('temp', exist_ok=True)
    
    # 保存为CSV
    csv_path = 'temp/test_data.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"✅ 创建测试CSV文件: {csv_path}")
    
    # 保存为Excel
    excel_path = 'temp/test_data.xlsx'
    df.to_excel(excel_path, index=False)
    print(f"✅ 创建测试Excel文件: {excel_path}")
    
    return csv_path, excel_path

def test_data_loading():
    """测试数据加载功能"""
    print("🔍 开始测试数据加载功能...")
    
    # 创建测试数据
    csv_path, excel_path = create_test_data()
    
    # 测试CSV加载
    print("\n📊 测试CSV文件加载:")
    try:
        df_csv = DataLoader.load_data(csv_path)
        print(f"  ✅ CSV加载成功: {df_csv.shape[0]} 行, {df_csv.shape[1]} 列")
        print(f"  📋 列名: {list(df_csv.columns)}")
        
        # 验证数据
        validation_result = DataValidator.validate_data(df_csv)
        print(f"  🔍 数据验证: {'通过' if validation_result['valid'] else '失败'}")
        if validation_result['issues']:
            print(f"  ⚠️ 问题: {', '.join(validation_result['issues'])}")
            
    except Exception as e:
        print(f"  ❌ CSV加载失败: {e}")
    
    # 测试Excel加载
    print("\n📊 测试Excel文件加载:")
    try:
        df_excel = DataLoader.load_data(excel_path)
        print(f"  ✅ Excel加载成功: {df_excel.shape[0]} 行, {df_excel.shape[1]} 列")
        print(f"  📋 列名: {list(df_excel.columns)}")
        
        # 验证数据
        validation_result = DataValidator.validate_data(df_excel)
        print(f"  🔍 数据验证: {'通过' if validation_result['valid'] else '失败'}")
        if validation_result['issues']:
            print(f"  ⚠️ 问题: {', '.join(validation_result['issues'])}")
            
    except Exception as e:
        print(f"  ❌ Excel加载失败: {e}")
    
    # 测试不支持的格式
    print("\n📊 测试不支持的格式:")
    try:
        DataLoader.load_data('test.unknown')
    except FileNotFoundError:
        print("  ✅ 正确识别文件不存在")
    except ValueError as e:
        print(f"  ✅ 正确识别不支持的格式: {e}")
    except Exception as e:
        print(f"  ❓ 其他错误: {e}")
    
    # 清理测试文件
    for file_path in [csv_path, excel_path]:
        if os.path.exists(file_path):
            os.remove(file_path)
    print("\n🧹 清理测试文件完成")

def test_supported_formats():
    """测试支持的格式"""
    print("\n📋 支持的文件格式:")
    formats = DataLoader.get_supported_formats()
    for fmt in formats:
        print(f"  ✅ {fmt}")

if __name__ == "__main__":
    print("🚀 开始数据加载测试")
    print("=" * 50)
    
    test_supported_formats()
    test_data_loading()
    
    print("\n" + "=" * 50)
    print("🎉 数据加载测试完成!")