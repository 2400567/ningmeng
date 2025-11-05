#!/usr/bin/env python3
"""
测试数据概览部分的修复
"""

import sys
import os
import logging
import pandas as pd
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_data_overview_fix():
    """测试数据概览修复"""
    try:
        logger.info("🔧 开始测试数据概览修复")
        
        # 导入必要的模块
        from src.report_generation.report_generator import create_advanced_report_generator
        
        # 创建测试数据（包含可能导致问题的数据）
        test_data = pd.DataFrame({
            'Product_ID': [1, 2, 3, None, 5],  # 包含None值
            'Sales': [100, 150, None, 180, 200],  # 包含None值
            'Price': [10.5, 15.0, 12.0, 18.0, None],  # 包含None值
            'Category': ['A', 'B', None, 'A', 'B']  # 包含None值
        })
        
        logger.info(f"📊 创建测试数据: {test_data.shape[0]} 行 x {test_data.shape[1]} 列")
        logger.info(f"数据包含 {test_data.isnull().sum().sum()} 个空值")
        
        # 创建报告生成器
        report_gen = create_advanced_report_generator()
        logger.info("✅ 报告生成器创建成功")
        
        # 测试场景1: 包含None值的file_info
        logger.info("\n🔬 场景1: file_info包含None值")
        problematic_file_info = {
            'file_name': None,  # 这可能导致错误
            'file_format': None  # 这也可能导致错误
        }
        
        try:
            output_path = "/workspaces/ningmeng/AI/temp/test_data_overview_none_fileinfo.docx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            saved_path = report_gen.generate_full_report(
                data=test_data,
                analysis_results={
                    'analysis_type': '测试分析',
                    'descriptive_stats': test_data.describe()
                },
                charts={},
                file_info=problematic_file_info,
                output_path=output_path
            )
            logger.info(f"✅ None file_info测试成功: {saved_path}")
        except Exception as e:
            logger.error(f"❌ None file_info测试失败: {str(e)}")
            raise
        
        # 测试场景2: file_info为None
        logger.info("\n🔬 场景2: file_info为None")
        try:
            output_path = "/workspaces/ningmeng/AI/temp/test_data_overview_no_fileinfo.docx"
            
            saved_path = report_gen.generate_full_report(
                data=test_data,
                analysis_results={
                    'analysis_type': '测试分析',
                    'descriptive_stats': test_data.describe()
                },
                charts={},
                file_info=None,  # 完全为None
                output_path=output_path
            )
            logger.info(f"✅ 无file_info测试成功: {saved_path}")
        except Exception as e:
            logger.error(f"❌ 无file_info测试失败: {str(e)}")
            raise
        
        # 测试场景3: 包含特殊字符和各种数据类型的数据
        logger.info("\n🔬 场景3: 特殊数据类型")
        special_data = pd.DataFrame({
            'Text': ['正常文本', '', None, '特殊字符@#$%', '中文测试'],
            'Numbers': [1, 0, None, float('inf'), -999],
            'Mixed': [1, 'text', None, True, [1, 2, 3]]
        })
        
        try:
            output_path = "/workspaces/ningmeng/AI/temp/test_data_overview_special.docx"
            
            saved_path = report_gen.generate_full_report(
                data=special_data,
                analysis_results={
                    'analysis_type': '特殊数据测试'
                },
                charts={},
                file_info={'file_name': '特殊数据.csv', 'file_format': 'CSV'},
                output_path=output_path
            )
            logger.info(f"✅ 特殊数据测试成功: {saved_path}")
        except Exception as e:
            logger.error(f"❌ 特殊数据测试失败: {str(e)}")
            raise
        
        logger.info("\n🎉 所有测试场景都成功完成！")
        
        # 检查生成的文件
        test_files = [
            "/workspaces/ningmeng/AI/temp/test_data_overview_none_fileinfo.docx",
            "/workspaces/ningmeng/AI/temp/test_data_overview_no_fileinfo.docx",
            "/workspaces/ningmeng/AI/temp/test_data_overview_special.docx"
        ]
        
        logger.info("📁 生成的测试文件:")
        for file_path in test_files:
            if os.path.exists(file_path):
                logger.info(f"   ✅ {file_path}")
            else:
                logger.warning(f"   ❌ {file_path}")
        
        return True
        
    except Exception as e:
        logger.exception(f"测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_data_overview_fix()
    if success:
        print("\n" + "="*60)
        print("🎊 数据概览修复测试成功完成！")
        print("="*60)
        print("\n修复内容:")
        print("✅ 修复了文档表格中 'NoneType' object is not iterable 错误")
        print("✅ 加强了对None值的安全处理")
        print("✅ 改进了file_info和列信息的处理")
        print("✅ 添加了详细的错误日志和异常处理")
        print("\n现在系统可以安全处理:")
        print("• None值的file_info字段")
        print("• 包含空值的数据列")
        print("• 各种特殊数据类型")
        print("• 缺失的文件信息")
    else:
        print("❌ 测试失败！")
        sys.exit(1)