# ningmeng

## 部署指南 (Streamlit Cloud)

如果在 Streamlit Cloud 构建时出现如下错误:

```
No solution found when resolving dependencies:
Because you require tqdm==4.67.1 and tqdm==4.66.1, we can conclude that your requirements are unsatisfiable.
```

或使用 Python 3.13 导致大量包需要从源码编译耗时/失败，请按以下步骤：

1. 确保仓库根目录存在 `runtime.txt` 并指定受支持版本，例如:
	```
	python-3.12.1
	```
	这样可避免使用尚未完全支持的 3.13 版本。
2. 在 `AI/requirements.txt` 中确保只保留一处 tqdm 版本 (当前已为 `tqdm==4.67.1`)；删除或注释重复条目。
3. 对可选大型依赖（xgboost / lightgbm / catboost / torch / tensorflow）保持注释状态以缩短构建。
4. 如果仍有构建超时，可创建一个精简文件 `requirements-core.txt` 仅含核心运行所需:
	```
	pandas==2.2.1
	numpy==1.26.4
	streamlit==1.33.0
	plotly==5.18.0
	scikit-learn==1.4.2
	openai==2.7.1
	pydantic==2.12.4
	tqdm==4.67.1
	PyYAML==6.0.1
	```
	然后在 Cloud 设置里改用该文件（或将其复制为根目录 `requirements.txt`）。

## 本地启动

增强版:
```
streamlit run AI/enhanced_app.py --server.port 8501
```

简单版:
```
streamlit run AI/simple_start.py --server.port 8502
```

## 错误自动上报

查看错误日志: `AI/error_reports/` 目录。可选改进: 指纹去重/严重级别标记。

---
此 README 补充了云端部署中最常见的版本冲突与 Python 版本问题的解决策略。