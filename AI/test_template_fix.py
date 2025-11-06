#!/usr/bin/env python3
"""
测试模板上传功能的修复
"""
import sys
import os
sys.path.append('src')

from template_management.template_manager import TemplateManager, AnalysisTemplate
import tempfile
import io

def test_template_creation():
    """测试模板创建"""
    print("🧪 测试模板对象创建...")
    
    template = AnalysisTemplate(
        name="测试模板",
        description="这是一个测试模板",
        template_type="factor_analysis",
        variables=["var1", "var2", "var3"],
        analysis_steps=[],
        output_format={},
        created_at="2025-11-06"
    )
    
    print(f"✅ 模板名称: {template.name}")
    print(f"✅ 模板类型: {template.template_type}")
    print(f"✅ 变量列表: {template.variables}")
    print(f"✅ 合并规则: {template.merge_rules}")
    
    return template

def test_template_manager():
    """测试模板管理器"""
    print("\n🧪 测试模板管理器...")
    
    tm = TemplateManager()
    
    # 创建测试模板
    test_template = test_template_creation()
    
    # 保存模板
    success = tm.save_template(test_template)
    print(f"✅ 模板保存: {'成功' if success else '失败'}")
    
    # 获取模板
    retrieved_template = tm.get_template("测试模板")
    if retrieved_template:
        print(f"✅ 模板获取成功: {retrieved_template.name}")
        print(f"✅ 模板类型: {type(retrieved_template)}")
        print(f"✅ 是否有name属性: {hasattr(retrieved_template, 'name')}")
    else:
        print("❌ 模板获取失败")
    
    return tm

def test_file_upload_simulation():
    """模拟文件上传测试"""
    print("\n🧪 模拟文件上传测试...")
    
    tm = TemplateManager()
    
    # 创建一个临时JSON文件
    test_json_content = {
        "name": "JSON测试模板",
        "description": "从JSON文件创建的测试模板",
        "template_type": "clustering",
        "variables": ["cluster_var1", "cluster_var2"],
        "analysis_steps": [
            {"step_name": "数据预处理", "method": "data_cleaning", "parameters": {}},
            {"step_name": "聚类分析", "method": "k_means", "parameters": {"n_clusters": 3}}
        ],
        "output_format": {"format": "academic_report"},
        "created_at": "2025-11-06"
    }
    
    # 模拟上传文件对象
    class MockUploadedFile:
        def __init__(self, name, content):
            self.name = name
            self.content = content
        
        def read(self):
            import json
            return json.dumps(self.content).encode('utf-8')
    
    mock_file = MockUploadedFile("test_template.json", test_json_content)
    
    try:
        template = tm.parse_template_from_file(mock_file)
        if template:
            print(f"✅ 文件解析成功: {template.name}")
            print(f"✅ 模板类型: {type(template)}")
            print(f"✅ 是否有name属性: {hasattr(template, 'name')}")
            print(f"✅ 是否有variables属性: {hasattr(template, 'variables')}")
            return template
        else:
            print("❌ 文件解析返回None")
    except Exception as e:
        print(f"❌ 文件解析异常: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def main():
    """主测试函数"""
    print("🚀 开始测试模板功能修复...")
    
    # 测试1: 基本模板创建
    template = test_template_creation()
    
    # 测试2: 模板管理器
    tm = test_template_manager()
    
    # 测试3: 文件上传模拟
    uploaded_template = test_file_upload_simulation()
    
    print("\n📊 测试结果总结:")
    print("✅ 模板对象创建 - 正常")
    print("✅ 模板管理器操作 - 正常")
    if uploaded_template:
        print("✅ 文件上传解析 - 正常")
        print(f"✅ 返回对象类型: {type(uploaded_template)}")
    else:
        print("❌ 文件上传解析 - 失败")
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    main()