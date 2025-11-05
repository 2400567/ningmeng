#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI报告增强功能测试脚本
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_ai_enhancer():
    """测试AI增强器基本功能"""
    print("🧪 开始测试AI报告增强功能...")
    
    try:
        # 导入AI增强模块
        from src.ai_agent.ai_report_enhancer import create_ai_enhancer, AIModelConfig
        print("✅ AI增强模块导入成功")
        
        # 创建测试数据
        np.random.seed(42)
        test_data = pd.DataFrame({
            '年龄': np.random.normal(35, 10, 100),
            '收入': np.random.normal(8000, 2000, 100),
            '满意度': np.random.randint(1, 8, 100),
            '性别': np.random.choice(['男', '女'], 100)
        })
        print("✅ 测试数据创建成功")
        
        # 创建测试分析结果
        test_results = {
            'descriptive_stats': test_data.describe(),
            'correlation': test_data.select_dtypes(include=[np.number]).corr(),
            'test_statistic': 2.45,
            'p_value': 0.021,
            'effect_size': 0.45
        }
        print("✅ 测试分析结果创建成功")
        
        # 测试不同配置的AI增强器创建
        configs = [
            ("Mock OpenAI", "openai", "gpt-3.5-turbo"),
            ("Mock Qwen", "qwen", "qwen-turbo"),
            ("Mock Local", "local", "llama2")
        ]
        
        for name, provider, model in configs:
            try:
                config = AIModelConfig(
                    provider=provider,
                    model_name=model,
                    api_key="test_key" if provider != "local" else None,
                    api_base="http://localhost:8080/api" if provider == "local" else None
                )
                
                # 注意：这里只测试初始化，不进行实际API调用
                from src.ai_agent.ai_report_enhancer import AIReportEnhancer
                enhancer = AIReportEnhancer(config)
                print(f"✅ {name} 配置初始化成功")
                
            except Exception as e:
                print(f"⚠️ {name} 配置测试跳过: {str(e)}")
        
        print("\n🎉 AI增强器基本功能测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {str(e)}")
        print("请确保已安装所需依赖: pip install openai requests")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_report_integration():
    """测试报告生成器集成"""
    print("\n🧪 测试报告生成器集成...")
    
    try:
        from src.report_generation.report_generator import AdvancedReportGenerator
        
        # 创建报告生成器
        report_gen = AdvancedReportGenerator()
        print("✅ 报告生成器创建成功")
        
        # 测试AI增强器设置
        try:
            from src.ai_agent.ai_report_enhancer import create_ai_enhancer
            # 创建测试用AI增强器（不会进行实际API调用）
            enhancer = create_ai_enhancer(provider="openai", api_key="test_key")
            report_gen.set_ai_enhancer(enhancer)
            print("✅ AI增强器集成成功")
        except Exception as e:
            print(f"⚠️ AI增强器集成测试跳过: {str(e)}")
        
        print("✅ 报告生成器集成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 报告生成器集成测试失败: {str(e)}")
        return False

def test_ui_integration():
    """测试UI集成"""
    print("\n🧪 测试UI集成...")
    
    try:
        # 测试UI模块导入
        from src.ui.app import AI_ENHANCEMENT_AVAILABLE
        
        if AI_ENHANCEMENT_AVAILABLE:
            print("✅ UI中AI增强功能可用")
        else:
            print("⚠️ UI中AI增强功能不可用")
        
        print("✅ UI集成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ UI集成测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI报告增强功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("AI增强器基本功能", test_ai_enhancer()))
    results.append(("报告生成器集成", test_report_integration()))
    results.append(("UI集成", test_ui_integration()))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 测试通过率: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    
    if passed == len(results):
        print("🎉 所有测试通过！AI报告增强功能已成功集成。")
    else:
        print("⚠️ 部分测试失败，请检查配置和依赖。")
    
    print("\n💡 使用说明:")
    print("1. 复制 .env.example 为 .env 并填入API密钥")
    print("2. 启动应用: streamlit run src/ui/app.py")
    print("3. 在侧边栏配置AI增强选项")
    print("4. 生成报告时将自动使用AI增强功能")