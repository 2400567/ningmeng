"""
简单测试当前的模板上传功能
"""
import sys
import os
sys.path.append('src')

def test_current_issue():
    """测试当前问题"""
    print("🔍 开始诊断当前问题...")
    
    # 导入相关模块
    try:
        from template_management.template_manager import TemplateManager, render_template_upload_ui
        print("✅ 模块导入成功")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return
    
    # 创建模板管理器
    try:
        tm = TemplateManager()
        print("✅ 模板管理器创建成功")
    except Exception as e:
        print(f"❌ 模板管理器创建失败: {e}")
        return
    
    # 检查现有模板
    try:
        templates = tm.get_available_templates()
        print(f"✅ 现有模板数量: {len(templates)}")
        for template_name in templates:
            template = tm.get_template(template_name)
            print(f"  - {template_name}: {type(template)}")
    except Exception as e:
        print(f"❌ 获取模板失败: {e}")
    
    print("\n🎯 诊断完成！")

if __name__ == "__main__":
    test_current_issue()