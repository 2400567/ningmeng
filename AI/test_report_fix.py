#!/usr/bin/env python3
"""
测试报告生成修复
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
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_report_fix.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_report_generation():
    """测试报告生成功能"""
    try:
        logger.info("开始测试报告生成功能")
        
        # 导入必要的模块
        from src.report_generation.report_generator import create_advanced_report_generator
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': [0.1, 0.2, 0.3, 0.4, 0.5]
        })
        
        # 创建测试分析结果（模拟可能为None的情况）
        test_analysis_results = {
            'analysis_type': '描述性统计分析',
            'descriptive_stats': test_data.describe(),
            'correlation': {
                'method': 'Pearson',
                'strong_correlations': [
                    {'feature1': 'A', 'feature2': 'B', 'correlation': 0.95}
                ]
            },
            'model_recommendations': [
                {
                    'name': '线性回归',
                    'score': 8.5,
                    'description': '适合线性关系的数据',
                    'reason': '数据呈现线性趋势'
                }
            ],
            'key_findings': [
                '数据质量良好',
                '特征A和B存在强相关性',
                '无明显异常值'
            ],
            'conclusions': [
                '数据适合进行回归分析',
                '建议使用线性模型'
            ],
            'recommendations': [
                '继续收集更多数据',
                '考虑特征工程'
            ]
        }
        
        logger.info("创建报告生成器")
        report_gen = create_advanced_report_generator()
        
        # 测试正常情况
        logger.info("测试正常情况下的报告生成")
        try:
            output_path = "/workspaces/ningmeng/AI/temp/test_report_normal.docx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            saved_path = report_gen.generate_full_report(
                data=test_data,
                analysis_results=test_analysis_results,
                charts={},
                file_info={'file_name': 'test_data.csv', 'file_format': 'CSV'},
                output_path=output_path
            )
            logger.info(f"正常情况测试成功，报告保存至: {saved_path}")
        except Exception as e:
            logger.error(f"正常情况测试失败: {str(e)}")
            raise
        
        # 测试异常情况1: analysis_results为None
        logger.info("测试analysis_results为None的情况")
        try:
            output_path = "/workspaces/ningmeng/AI/temp/test_report_none_analysis.docx"
            saved_path = report_gen.generate_full_report(
                data=test_data,
                analysis_results=None,
                charts={},
                file_info={'file_name': 'test_data.csv', 'file_format': 'CSV'},
                output_path=output_path
            )
            logger.info(f"None analysis_results测试成功，报告保存至: {saved_path}")
        except Exception as e:
            logger.error(f"None analysis_results测试失败: {str(e)}")
            raise
        
        # 测试异常情况2: 空的analysis_results
        logger.info("测试空analysis_results的情况")
        try:
            output_path = "/workspaces/ningmeng/AI/temp/test_report_empty_analysis.docx"
            saved_path = report_gen.generate_full_report(
                data=test_data,
                analysis_results={},
                charts={},
                file_info={'file_name': 'test_data.csv', 'file_format': 'CSV'},
                output_path=output_path
            )
            logger.info(f"空analysis_results测试成功，报告保存至: {saved_path}")
        except Exception as e:
            logger.error(f"空analysis_results测试失败: {str(e)}")
            raise
        
        # 测试异常情况3: 包含None值的analysis_results
        logger.info("测试包含None值的analysis_results")
        try:
            problematic_analysis_results = {
                'analysis_type': None,
                'descriptive_stats': None,
                'correlation': None,
                'model_recommendations': None,
                'key_findings': None,
                'conclusions': None,
                'recommendations': None
            }
            
            output_path = "/workspaces/ningmeng/AI/temp/test_report_none_values.docx"
            saved_path = report_gen.generate_full_report(
                data=test_data,
                analysis_results=problematic_analysis_results,
                charts={},
                file_info={'file_name': 'test_data.csv', 'file_format': 'CSV'},
                output_path=output_path
            )
            logger.info(f"None值analysis_results测试成功，报告保存至: {saved_path}")
        except Exception as e:
            logger.error(f"None值analysis_results测试失败: {str(e)}")
            raise
        
        logger.info("所有测试都通过了！")
        return True
        
    except Exception as e:
        logger.exception(f"测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_report_generation()
    if success:
        print("✅ 报告生成修复测试成功！")
    else:
        print("❌ 报告生成修复测试失败！")
        sys.exit(1)