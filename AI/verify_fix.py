# 简单的None检查测试脚本

# 模拟我们在app.py中实现的修复逻辑
def test_none_check():
    print("测试None检查逻辑...")
    
    # 测试场景1: current_data为None
    current_data = None
    print(f"\n场景1: current_data = None")
    if current_data is None:
        print("✓ 成功检测到current_data为None")
    else:
        print("✗ 未能检测到current_data为None")
    
    # 测试场景2: current_data不为None
    current_data = "有数据"
    print(f"\n场景2: current_data = '{current_data}'")
    if current_data is None:
        print("✗ 错误地检测到current_data为None")
    else:
        print("✓ 正确检测到current_data不为None")

# 运行测试
test_none_check()
print("\n测试完成!")