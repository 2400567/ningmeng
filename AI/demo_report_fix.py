#!/usr/bin/env python3
"""
演示修复后的报告生成功能
"""

import sys
import os
import logging
import pandas as pd
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置简单日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def demo_fixed_report_generation():
    """演示修复后的报告生成功能"""
    try:
        logger.info("🚀 开始演示修复后的报告生成功能")
        
        # 导入必要的模块
        from src.report_generation.report_generator import create_advanced_report_generator
        
        # 创建演示数据
        demo_data = pd.DataFrame({
            'Product_ID': [1, 2, 3, 4, 5],
            'Sales': [100, 150, 120, 180, 200],
            'Price': [10.5, 15.0, 12.0, 18.0, 20.0],
            'Rating': [4.2, 4.5, 4.1, 4.7, 4.8]
        })
        
        logger.info(f"📊 创建演示数据: {demo_data.shape[0]} 行 x {demo_data.shape[1]} 列")
        
        # 创建报告生成器
        report_gen = create_advanced_report_generator()
        logger.info("✅ 报告生成器创建成功")
        
        # 演示场景1: 完整的分析结果
        logger.info("\n🔬 场景1: 完整的分析结果")
        complete_analysis = {
            'analysis_type': '产品销售分析',
            'descriptive_stats': demo_data.describe(),
            'correlation': {
                'method': 'Pearson',
                'strong_correlations': [
                    {'feature1': 'Sales', 'feature2': 'Price', 'correlation': 0.89},
                    {'feature1': 'Sales', 'feature2': 'Rating', 'correlation': 0.76}
                ]
            },
            'model_recommendations': [
                {
                    'name': '线性回归模型',
                    'score': 8.5,
                    'description': '适合预测产品销售量',
                    'reason': '销量与价格、评分呈现线性关系'
                }
            ],
            'key_findings': [
                '产品销量与价格呈正相关',
                '高评分产品销量更好',
                '产品定价策略合理'
            ],
            'conclusions': [
                '数据表明价格策略有效',
                '应重点关注产品质量提升'
            ],
            'recommendations': [
                '继续优化产品质量',
                '适当提高高评分产品价格'
            ]
        }
        
        output_path = "/workspaces/ningmeng/AI/temp/demo_complete_report.docx"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        saved_path = report_gen.generate_full_report(
            data=demo_data,
            analysis_results=complete_analysis,
            charts={},
            file_info={'file_name': 'product_sales.csv', 'file_format': 'CSV'},
            output_path=output_path
        )
        logger.info(f"✅ 完整报告生成成功: {saved_path}")
        
        # 演示场景2: 空的分析结果（之前会出错的情况）
        logger.info("\n🔬 场景2: 空的分析结果（修复前会出错）")
        
        output_path = "/workspaces/ningmeng/AI/temp/demo_empty_report.docx"
        saved_path = report_gen.generate_full_report(
            data=demo_data,
            analysis_results=None,  # 这之前会导致 'NoneType' object is not iterable 错误
            charts={},
            file_info={'file_name': 'product_sales.csv', 'file_format': 'CSV'},
            output_path=output_path
        )
        logger.info(f"✅ 空分析结果报告生成成功: {saved_path}")
        
        # 演示场景3: 部分缺失的分析结果
        logger.info("\n🔬 场景3: 部分缺失的分析结果")
        
        partial_analysis = {
            'analysis_type': '基础分析',
            'descriptive_stats': demo_data.describe(),
            # 其他字段故意缺失或为None
            'correlation': None,
            'model_recommendations': [],
            'key_findings': None,
            'conclusions': [],
            'recommendations': None
        }
        
        output_path = "/workspaces/ningmeng/AI/temp/demo_partial_report.docx"
        saved_path = report_gen.generate_full_report(
            data=demo_data,
            analysis_results=partial_analysis,
            charts={},
            file_info={'file_name': 'product_sales.csv', 'file_format': 'CSV'},
            output_path=output_path
        )
        logger.info(f"✅ 部分缺失报告生成成功: {saved_path}")
        
        logger.info("\n🎉 所有演示场景都成功完成！")
        logger.info("📁 生成的报告文件:")
        for file in [
            "/workspaces/ningmeng/AI/temp/demo_complete_report.docx",
            "/workspaces/ningmeng/AI/temp/demo_empty_report.docx",
            "/workspaces/ningmeng/AI/temp/demo_partial_report.docx"
        ]:
            if os.path.exists(file):
                logger.info(f"   ✅ {file}")
            else:
                logger.warning(f"   ❌ {file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 演示过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = demo_fixed_report_generation()
    if success:
        print("\n" + "="*50)
        print("🎊 报告生成修复演示成功完成！")
        print("="*50)
        print("\n修复内容总结:")
        print("✅ 修复了 'NoneType' object is not iterable 错误")
        print("✅ 添加了详细的错误日志记录")
        print("✅ 增强了对None值和空值的处理")
        print("✅ 改进了分析结果的安全性检查")
        print("✅ 提供了详细的错误追踪信息")
        print("\n现在系统可以正常处理:")
        print("• 完整的分析结果")
        print("• 空的或None的分析结果")
        print("• 部分缺失的分析结果")
        print("• 格式不正确的分析结果")
    else:
        print("❌ 演示失败！")
        sys.exit(1)