#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI连接详细测试脚本
提供全面的AI连接测试和诊断信息
"""

import sys
import os
import traceback
import requests
from pathlib import Path
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_agent.ai_report_enhancer import AIModelConfig, AIReportEnhancer

def test_network_connectivity():
    """测试基础网络连接"""
    print("🌐 测试网络连接...")
    
    test_urls = [
        "https://api.openai.com",
        "https://www.google.com",
        "https://httpbin.org/get"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"  ✅ {url} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url} - 错误: {str(e)}")

def test_openai_api_access():
    """测试OpenAI API访问"""
    print("\n🔑 测试OpenAI API访问...")
    
    try:
        # 测试不需要认证的端点
        response = requests.get("https://api.openai.com/v1/models", timeout=10)
        if response.status_code == 401:
            print("  ✅ OpenAI API可访问 (返回认证错误是正常的)")
        else:
            print(f"  ⚠️ OpenAI API响应异常 - 状态码: {response.status_code}")
    except Exception as e:
        print(f"  ❌ OpenAI API不可访问 - 错误: {str(e)}")

def test_ai_enhancer_creation():
    """测试AI增强器创建"""
    print("\n🤖 测试AI增强器创建...")
    
    try:
        # 使用测试配置
        config = AIModelConfig(
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key='test-key-for-init-test',
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"  📋 配置信息:")
        print(f"    - 提供商: {config.provider}")
        print(f"    - 模型: {config.model_name}")
        print(f"    - API密钥: {'已设置' if config.api_key else '未设置'}")
        print(f"    - API地址: {config.api_base or '默认地址'}")
        
        # 创建增强器实例
        enhancer = AIReportEnhancer(config)
        print("  ✅ AI增强器创建成功")
        
        return enhancer, config
        
    except Exception as e:
        print(f"  ❌ AI增强器创建失败:")
        print(f"    错误类型: {type(e).__name__}")
        print(f"    错误信息: {str(e)}")
        print(f"    详细堆栈:")
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                print(f"      {line}")
        return None, None

def test_with_real_api_key():
    """使用真实API密钥测试"""
    print("\n🔐 真实API密钥测试...")
    
    # 从环境变量获取API密钥
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("  ⚠️ 未设置OPENAI_API_KEY环境变量")
        print("  💡 要进行完整测试，请设置环境变量:")
        print("     export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        config = AIModelConfig(
            provider='openai',
            model_name='gpt-3.5-turbo',
            api_key=api_key,
            max_tokens=50,
            temperature=0.7
        )
        
        enhancer = AIReportEnhancer(config)
        print("  ✅ 使用真实API密钥创建增强器成功")
        
        # 尝试实际调用
        test_prompt = "请回复'测试成功'"
        print("  🔄 尝试调用AI模型...")
        response = enhancer._call_ai_model(test_prompt)
        print(f"  ✅ AI模型调用成功!")
        print(f"    响应: {response[:100]}...")
        
    except Exception as e:
        print(f"  ❌ 真实API测试失败:")
        print(f"    错误信息: {str(e)}")

def run_comprehensive_test():
    """运行全面测试"""
    print("🔍 AI连接全面诊断测试")
    print("=" * 50)
    
    # 1. 网络连接测试
    test_network_connectivity()
    
    # 2. OpenAI API访问测试
    test_openai_api_access()
    
    # 3. AI增强器创建测试
    enhancer, config = test_ai_enhancer_creation()
    
    # 4. 真实API密钥测试
    test_with_real_api_key()
    
    print("\n" + "=" * 50)
    print("🎯 测试总结:")
    print("  - 如果看到网络连接错误，请检查网络设置")
    print("  - 如果看到API访问错误，请检查防火墙和代理设置")
    print("  - 如果增强器创建失败，请检查代码依赖")
    print("  - 要完整测试AI功能，请设置有效的OPENAI_API_KEY")
    
    print("\n💡 在Streamlit应用中进行测试:")
    print("  1. 在侧边栏配置AI设置")
    print("  2. 点击'测试AI连接'按钮")
    print("  3. 查看详细错误信息和建议")

if __name__ == "__main__":
    run_comprehensive_test()