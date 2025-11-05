import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="AI数据分析系统",
    page_icon="📊",
    layout="wide"
)

st.title("🎉 AI数据分析系统")
st.success("✅ 系统运行正常！")

st.markdown("""
## 🚀 欢迎使用AI数据分析系统

这是一个测试页面，用于验证系统是否正常运行。

### 📋 系统状态
- **服务状态**: 正常运行 ✅
- **端口**: 8501
- **环境**: GitHub Codespaces

### 🎯 功能测试
""")

# 简单的功能测试
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 数据生成测试")
    if st.button("生成测试数据"):
        data = pd.DataFrame({
            'A': np.random.randn(100),
            'B': np.random.randn(100),
            'C': np.random.randn(100)
        })
        st.dataframe(data.head())
        st.line_chart(data)

with col2:
    st.subheader("📈 图表测试")
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c']
    )
    st.line_chart(chart_data)

st.info("💡 如果您看到此页面，说明网络连接正常！您可以开始使用完整的AI数据分析功能。")

# 显示一些系统信息
st.markdown("---")
st.subheader("🔧 系统信息")
st.write(f"Streamlit版本: {st.__version__}")
st.write(f"Pandas版本: {pd.__version__}")
st.write(f"Numpy版本: {np.__version__}")

st.balloons()