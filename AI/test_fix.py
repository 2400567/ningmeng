import sys
sys.path.insert(0, '.')
from src.ui.app import AppState

# 测试AppState初始化和None检查逻辑
print("开始测试修复...")

# 模拟Streamlit会话状态
class MockSessionState:
    def __init__(self):
        self.data = None
        self.processed_data = None
    
    def get(self, key, default=None):
        return getattr(self, key, default)

# 模拟current_data获取逻辑
def test_current_data():
    print("\n测试1: 当data和processed_data都是None时")
    mock_state = MockSessionState()
    current_data = mock_state.get('processed_data', mock_state.data)
    print(f"current_data is None: {current_data is None}")
    print("修复逻辑应该会检测到这个情况并阻止select_dtypes调用")
    
    print("\n测试2: 当data不为None时")
    mock_state.data = "测试数据"
    current_data = mock_state.get('processed_data', mock_state.data)
    print(f"current_data: {current_data}")
    print("修复逻辑应该允许继续执行")

# 运行测试
test_current_data()
print("\n测试完成！")