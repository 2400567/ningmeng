#!/usr/bin/env python3
"""
增强版AI数据分析系统功能验证脚本
验证所有核心模块和功能是否正常工作
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_core_imports():
    """测试核心模块导入"""
    print("🔧 测试核心模块导入:")
    
    modules = [
        ('src.data_processing.data_loader', 'DataLoader'),
        ('src.data_processing.spss_analyzer', 'SPSSAnalyzer'),
        ('src.ai_agent.academic_engine', 'AcademicAnalysisEngine'),
        ('src.ai_agent.literature_search', 'LiteratureSearchEngine'),
        ('src.report_generation.report_templates', 'ReportTemplateManager'),
        ('src.visualization.advanced_visualizer', 'AdvancedVisualizer'),
        ('src.config', 'CONFIG')
    ]
    
    success_count = 0
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {module_name}.{class_name} - 导入失败: {e}")
        except AttributeError as e:
            print(f"  ❌ {module_name}.{class_name} - 属性错误: {e}")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name} - 其他错误: {e}")
    
    print(f"  📊 成功导入: {success_count}/{len(modules)} 个模块")
    return success_count == len(modules)

def test_data_processing():
    """测试数据处理功能"""
    print("\n📊 测试数据处理功能:")
    
    try:
        from src.data_processing.data_loader import DataLoader
        from src.data_processing.spss_analyzer import SPSSAnalyzer
        
        # 创建测试数据
        np.random.seed(42)
        test_data = pd.DataFrame({
            'group': ['A', 'B'] * 50,
            'score1': np.random.normal(100, 15, 100),
            'score2': np.random.normal(85, 12, 100),
            'age': np.random.randint(18, 65, 100),
            'category': np.random.choice(['X', 'Y', 'Z'], 100)
        })
        
        # 测试SPSS分析器
        analyzer = SPSSAnalyzer(test_data)
        
        # 描述性统计
        desc_stats = analyzer.descriptive_statistics()
        print(f"  ✅ 描述性统计: {len(desc_stats)} 个变量")
        
        # 相关性分析
        corr_result = analyzer.correlation_analysis()
        if corr_result:
            print(f"  ✅ 相关性分析: {corr_result['correlation_matrix'].shape}")
        
        # T检验
        t_test_result = analyzer.t_test_independent('score1', 'group')
        if t_test_result:
            print(f"  ✅ T检验: p值 = {t_test_result['p_value']:.4f}")
        
        return True
    except Exception as e:
        print(f"  ❌ 数据处理测试失败: {e}")
        return False

def test_ai_features():
    """测试AI功能"""
    print("\n🤖 测试AI功能:")
    
    try:
        from src.ai_agent.academic_engine import AcademicAnalysisEngine
        from src.ai_agent.literature_search import LiteratureSearchEngine
        
        # 测试学术引擎
        academic_engine = AcademicAnalysisEngine()
        print("  ✅ AcademicAnalysisEngine 初始化成功")
        
        # 测试文献检索
        literature_engine = LiteratureSearchEngine()
        print("  ✅ LiteratureSearchEngine 初始化成功")
        
        # 模拟文献检索
        search_results = literature_engine.search_literature(
            ['机器学习', '数据分析'], 
            ['cnki'], 
            max_results=5,
            year_range=(2020, 2024)
        )
        
        if search_results:
            total_papers = sum(len(papers) for papers in search_results.values())
            print(f"  ✅ 文献检索测试: 找到 {total_papers} 篇文献")
        
        return True
    except Exception as e:
        print(f"  ❌ AI功能测试失败: {e}")
        return False

def test_visualization():
    """测试可视化功能"""
    print("\n📈 测试可视化功能:")
    
    try:
        from src.visualization.advanced_visualizer import AdvancedVisualizer
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'x': np.random.randn(100),
            'y': np.random.randn(100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        # 测试可视化器
        visualizer = AdvancedVisualizer()
        print("  ✅ AdvancedVisualizer 初始化成功")
        
        # 测试相关性热力图
        fig = visualizer.create_correlation_heatmap(test_data, ['x', 'y'])
        if fig:
            print("  ✅ 相关性热力图创建成功")
        
        return True
    except Exception as e:
        print(f"  ❌ 可视化测试失败: {e}")
        return False

def test_report_templates():
    """测试报告模板功能"""
    print("\n📄 测试报告模板功能:")
    
    try:
        from src.report_generation.report_templates import ReportTemplateManager
        
        # 测试模板管理器
        template_manager = ReportTemplateManager()
        templates = template_manager.list_available_templates()
        print(f"  ✅ 可用模板: {len(templates)} 个")
        
        # 测试获取模板
        academic_template = template_manager.get_template('academic_paper')
        if academic_template:
            print(f"  ✅ 学术论文模板: {len(academic_template['structure'])} 个章节")
        
        return True
    except Exception as e:
        print(f"  ❌ 报告模板测试失败: {e}")
        return False

def test_system_config():
    """测试系统配置"""
    print("\n⚙️ 测试系统配置:")
    
    try:
        from src.config import CONFIG, get_config
        
        # 测试配置读取
        app_config = get_config('app')
        print(f"  ✅ 应用配置: {app_config.get('title', 'Unknown')}")
        
        ai_config = get_config('ai')
        print(f"  ✅ AI配置: {len(ai_config.get('providers', {}))} 个提供商")
        
        spss_config = get_config('spss')
        print(f"  ✅ SPSS配置: 显著性水平 {spss_config.get('significance_level', 0.05)}")
        
        return True
    except Exception as e:
        print(f"  ❌ 系统配置测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始增强版AI数据分析系统功能验证")
    print("=" * 60)
    
    tests = [
        ("核心模块导入", test_core_imports),
        ("数据处理功能", test_data_processing),
        ("AI功能", test_ai_features),
        ("可视化功能", test_visualization),
        ("报告模板功能", test_report_templates),
        ("系统配置", test_system_config)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
    
    print("\n" + "=" * 60)
    print("📊 验证结果总结:")
    print("=" * 60)
    
    print(f"✅ 通过测试: {passed_tests}/{total_tests}")
    print(f"📈 成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有功能验证通过！系统状态良好！")
        print("🌐 您可以安全地使用增强版AI数据分析系统")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} 个测试失败")
        print("💡 请检查相关模块并修复问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)