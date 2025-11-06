#!/usr/bin/env python3
"""
详细错误诊断工具
用于分析和解决数据读取失败问题
"""

import sys
import os
import traceback
from pathlib import Path

# 添加src路径
sys.path.append('src')

def detailed_error_diagnosis():
    """详细的错误诊断"""
    print("🔍 开始详细错误诊断...")
    print("=" * 60)
    
    # 1. 检查模块导入
    print("\n📦 1. 模块导入测试:")
    try:
        from template_management.template_manager import TemplateManager, AnalysisTemplate, render_template_upload_ui
        print("✅ 所有模块导入成功")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        traceback.print_exc()
        return
    
    # 2. 创建模板管理器
    print("\n🏗️ 2. 模板管理器创建测试:")
    try:
        tm = TemplateManager()
        print("✅ 模板管理器创建成功")
    except Exception as e:
        print(f"❌ 模板管理器创建失败: {e}")
        traceback.print_exc()
        return
    
    # 3. 检查现有模板
    print("\n📋 3. 现有模板检查:")
    try:
        templates = tm.get_available_templates()
        print(f"✅ 发现 {len(templates)} 个现有模板:")
        
        for i, template_name in enumerate(templates, 1):
            try:
                template_obj = tm.get_template(template_name)
                print(f"  {i}. {template_name}")
                print(f"     - 类型: {type(template_obj)}")
                print(f"     - 是否有name属性: {hasattr(template_obj, 'name')}")
                if hasattr(template_obj, 'name'):
                    print(f"     - name值: {template_obj.name}")
                if hasattr(template_obj, '__dict__'):
                    print(f"     - 属性列表: {list(template_obj.__dict__.keys())}")
            except Exception as e:
                print(f"  {i}. {template_name} - ❌ 获取失败: {e}")
                
    except Exception as e:
        print(f"❌ 获取模板列表失败: {e}")
        traceback.print_exc()
    
    # 4. 模拟文件上传测试
    print("\n📤 4. 文件上传模拟测试:")
    try:
        # 创建一个模拟的JSON模板文件
        import json
        from io import StringIO
        
        test_template_data = {
            "name": "诊断测试模板",
            "description": "用于错误诊断的测试模板",
            "template_type": "custom",
            "variables": ["test_var1", "test_var2"],
            "analysis_steps": [
                {"step_name": "测试步骤", "method": "test_method", "parameters": {}}
            ],
            "output_format": {"format": "test"},
            "created_at": "2025-11-06"
        }
        
        # 模拟上传文件对象
        class MockFile:
            def __init__(self, name, content):
                self.name = name
                self.content = content
            
            def read(self):
                return json.dumps(self.content).encode('utf-8')
        
        mock_file = MockFile("test_template.json", test_template_data)
        
        # 测试解析
        parsed_template = tm.parse_template_from_file(mock_file)
        
        if parsed_template:
            print("✅ 文件解析成功:")
            print(f"  - 返回类型: {type(parsed_template)}")
            print(f"  - 是否有name属性: {hasattr(parsed_template, 'name')}")
            if hasattr(parsed_template, 'name'):
                print(f"  - name值: {parsed_template.name}")
            print(f"  - 字符串表示: {repr(parsed_template)}")
        else:
            print("❌ 文件解析返回None")
            
    except Exception as e:
        print(f"❌ 文件上传模拟失败: {e}")
        traceback.print_exc()
    
    # 5. 检查session state模拟
    print("\n💾 5. Session State 模拟测试:")
    try:
        # 模拟streamlit session state
        class MockSessionState:
            def __init__(self):
                self.data = {}
            
            def get(self, key, default=None):
                return self.data.get(key, default)
            
            def __setitem__(self, key, value):
                self.data[key] = value
            
            def __getitem__(self, key):
                return self.data[key]
        
        mock_st_session = MockSessionState()
        
        # 测试不同的session state值
        test_cases = [
            ("现有模板名称", "测试模板"),
            ("无效模板名称", "不存在的模板"),
            ("None值", None),
            ("空字符串", ""),
        ]
        
        for case_name, test_value in test_cases:
            print(f"\n  测试用例: {case_name}")
            mock_st_session['selected_template'] = test_value
            
            selected_name = mock_st_session.get('selected_template')
            print(f"    - selected_template: {repr(selected_name)}")
            
            if selected_name:
                try:
                    result = tm.get_template(selected_name)
                    print(f"    - get_template结果: {type(result)} - {repr(result)}")
                except Exception as e:
                    print(f"    - get_template错误: {e}")
            else:
                print(f"    - 跳过get_template (值为空)")
        
    except Exception as e:
        print(f"❌ Session State 测试失败: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 诊断完成!")
    
    # 6. 问题总结和建议
    print("\n📊 问题总结和建议:")
    print("1. 如果所有测试都通过，问题可能在于:")
    print("   - Streamlit的缓存机制")
    print("   - 浏览器端的状态缓存")
    print("   - 并发状态更新冲突")
    
    print("\n2. 建议的解决步骤:")
    print("   a. 清除所有Python缓存: rm -rf __pycache__ src/__pycache__ src/*/__pycache__")
    print("   b. 清除Streamlit缓存: rm -rf .streamlit")
    print("   c. 重启应用")
    print("   d. 清除浏览器缓存")
    
    print("\n3. 如果问题仍然存在:")
    print("   - 检查具体的错误行号和调用栈")
    print("   - 添加更多调试输出")
    print("   - 考虑使用session state重置")

if __name__ == "__main__":
    detailed_error_diagnosis()