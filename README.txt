NINGMENG 最小运行说明
=====================

1. Python 版本
   - 使用 pyproject.toml 中 requires-python: >=3.12,<3.13
   - 若本地未安装，建议安装 3.12.x

2. 安装核心依赖
   - 使用 requirements.txt 或精简 requirements-base.txt
   示例：
     pip install -r requirements-base.txt
   或完整：
     pip install -r requirements.txt

3. 启动应用 (Streamlit)
   增强版：
     streamlit run AI/enhanced_app.py --server.port 8501
   简化版：
     streamlit run AI/simple_start.py --server.port 8502

4. 生成测试数据（若需要）
   运行：
     python AI/create_test_data.py
   输出文件：AI/comprehensive_test_data.csv （若文件缺失可再次运行脚本生成）

5. 常见目录说明
   - scripts/: 实用脚本（如环境检查 scripts/check_env.py）
   - AI/src/: 主代码模块（数据处理、可视化、报告生成等）
   - templates/: 模型与报告模板（不要删除）
   - temp/: 临时输出目录（可清空）

6. 已忽略/不再提交的内容
   - 虚拟环境: venv/ .venv/ AI/venv/
   - 缓存与字节码: __pycache__/ *.pyc
   - 日志与临时: *.log temp/ AI/temp/
   - 清理的演示/备份文件: examples/ demo_template.txt launch_app.py.bak 等

7. 依赖版本统一要点
   - pandas==2.1.3, numpy==1.26.4, tqdm==4.67.1
   - 若需要新增大型库 (torch / tensorflow / prophet) 建议放入 requirements-optional.txt

8. 恢复已删除的文档
   若需要找回被删除的历史 Markdown 文档：
     git log --oneline
     # 找到删除前提交 <COMMIT_ID>
     git checkout <COMMIT_ID> -- README.md  # 示例（文件已删除）

9. 清理与重建
   - 清空临时目录: rm -rf temp/*
   - 重新生成数据: python AI/create_test_data.py

10. 问题排查快速指令
    - 版本检查：python scripts/check_env.py
    - 依赖缺失：pip install -r requirements-base.txt

11. 部署提示（Streamlit Cloud）
    - 若平台忽略 runtime.txt 导致使用 3.13，可尝试保留 pyproject.toml 并指定 Python 版本
    - 如遇构建超时可先仅使用 requirements-base.txt 构建，再追加安装 optional

12. 下一步可选改进
    - 添加 CI (GitHub Actions) 自动测试与依赖锁定
    - 使用 pip-tools 生成锁文件 (requirements.lock)
    - 将生成数据脚本加入 Makefile 或 invoke 任务体系

(自动生成最小 README.txt，后续可按需扩展)
