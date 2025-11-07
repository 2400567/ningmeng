# ningmeng

## 部署指南 (Streamlit Cloud)

如果在 Streamlit Cloud 构建时出现依赖冲突（例如早期曾出现的 `tqdm==4.67.1` 与 `tqdm==4.66.1` 版本同时被解析）或使用 Python 3.13 导致大量包从源码编译耗时/失败，请按以下步骤：

1. 确保仓库根目录存在 `runtime.txt` 并指定受支持版本，例如:
	```
	python-3.12.1
	```
	这样可避免使用尚未完全支持的 3.13 版本。
2. 在 `AI/requirements.txt` 中确保只保留一处 tqdm 版本 (当前已为 `tqdm==4.67.1`)；删除或注释重复条目。
3. 对可选大型依赖（xgboost / lightgbm / catboost / torch / tensorflow）保持注释状态以缩短构建。
4. 如果仍有构建超时，可使用已新增的拆分文件：
	- `requirements-base.txt`：核心依赖（快速构建）
	- `requirements-optional.txt`：扩展/重量依赖（按需）

	Cloud 上设置优先指向 `requirements-base.txt`，完成构建后再在运行环境里追加安装可选包：
	```
	pip install -r requirements-optional.txt
	```

5. 保持多处 requirements 的版本统一（已经统一 pandas==2.1.3 / numpy==1.26.4 / tqdm==4.67.1）。避免一个文件使用 `>=` 而另一个固定旧版造成冲突。

## 本地启动

增强版:
```
streamlit run AI/enhanced_app.py --server.port 8501
```

简单版:
```
streamlit run AI/simple_start.py --server.port 8502
```

## 环境快速自检

运行脚本打印关键依赖版本：
```
python scripts/check_env.py
```

若出现 `NOT INSTALLED` 可确认对应包是否在 base 或 optional 文件中并执行：
```
pip install -r requirements-base.txt
# 或/以及
pip install -r requirements-optional.txt
```

## 错误自动上报

查看错误日志: `AI/error_reports/` 目录。可选改进: 指纹去重/严重级别标记。

---
此 README 补充了云端部署中最常见的版本冲突与 Python 版本问题的解决策略。