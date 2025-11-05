#!/bin/bash

echo "🚀 启动AI数据分析系统"
echo "========================"

# 检查是否有正在运行的服务
if pgrep -f "streamlit" > /dev/null; then
    echo "⚠️  检测到正在运行的Streamlit服务，正在停止..."
    pkill -f streamlit
    sleep 2
fi

# 切换到项目目录
cd /workspaces/ningmeng/AI

# 启动服务
echo "🌐 启动Web界面..."
/home/codespace/.python/current/bin/python -m streamlit run src/ui/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --server.enableWebsocketCompression false

echo "✅ 服务已启动"
echo "📍 访问地址: http://localhost:8501"
echo "💡 在VS Code中："
echo "   1. 点击底部'端口'选项卡"
echo "   2. 找到端口8501"
echo "   3. 点击🌐图标访问"