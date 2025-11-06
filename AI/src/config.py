"""
系统配置文件
包含增强版AI数据分析系统的所有配置选项
"""

import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent.parent.absolute()
TEMP_DIR = BASE_DIR / "temp"
DOCS_DIR = BASE_DIR / "docs"
EXAMPLES_DIR = BASE_DIR / "examples"

# 创建必要目录
for directory in [TEMP_DIR, DOCS_DIR, EXAMPLES_DIR]:
    directory.mkdir(exist_ok=True)

# 应用配置
APP_CONFIG = {
    "title": "AI智能数据分析大模型系统 Enhanced",
    "version": "2.0.0",
    "description": "集成SPSS分析、学术报告、文献检索的专业数据分析平台",
    "author": "AI Data Analysis Team",
    "port": 8501,
    "host": "localhost"
}

# AI配置
AI_CONFIG = {
    "default_provider": "通义千问",
    "providers": {
        "通义千问": {
            "api_key": os.getenv("QWEN_API_KEY", ""),
            "base_url": "https://dashscope.aliyuncs.com/api/v1/",
            "model": "qwen-plus"
        },
        "OpenAI": {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "base_url": "https://api.openai.com/v1/",
            "model": "gpt-3.5-turbo"
        },
        "本地模型": {
            "api_key": "",
            "base_url": "http://localhost:11434/",
            "model": "llama2"
        }
    },
    "max_tokens": 4000,
    "temperature": 0.7,
    "timeout": 30
}

# 数据分析配置
ANALYSIS_CONFIG = {
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    "supported_formats": [".csv", ".xlsx", ".xls", ".json"],
    "max_rows": 1000000,
    "max_columns": 1000,
    "cache_results": True,
    "cache_duration": 3600  # 1小时
}

# SPSS分析配置
SPSS_CONFIG = {
    "significance_level": 0.05,
    "confidence_level": 0.95,
    "missing_value_threshold": 0.3,
    "outlier_method": "iqr",
    "correlation_methods": ["pearson", "spearman", "kendall"],
    "default_plots": True,
    "report_format": "academic"
}

# 可视化配置
VISUALIZATION_CONFIG = {
    "default_style": "academic",
    "styles": {
        "academic": {
            "palette": "Set2",
            "figure_size": (10, 6),
            "dpi": 300,
            "font_family": "serif",
            "font_size": 12
        },
        "business": {
            "palette": "viridis",
            "figure_size": (12, 8),
            "dpi": 300,
            "font_family": "sans-serif",
            "font_size": 11
        },
        "modern": {
            "palette": "husl",
            "figure_size": (10, 6),
            "dpi": 300,
            "font_family": "sans-serif",
            "font_size": 10
        }
    },
    "save_formats": ["png", "pdf", "svg"],
    "interactive_backend": "plotly"
}

# 报告生成配置
REPORT_CONFIG = {
    "templates_dir": TEMP_DIR / "templates",
    "output_dir": TEMP_DIR / "reports",
    "default_template": "academic_paper",
    "citation_styles": ["APA", "MLA", "Chicago", "GB/T 7714"],
    "default_citation_style": "APA",
    "max_report_length": 50000,  # 字符数
    "include_figures": True,
    "include_tables": True,
    "auto_number_sections": True
}

# 文献检索配置
LITERATURE_CONFIG = {
    "databases": {
        "cnki": {
            "name": "知网(CNKI)",
            "url": "https://kns.cnki.net/",
            "enabled": True,
            "max_results": 50
        },
        "wanfang": {
            "name": "万方数据",
            "url": "https://www.wanfangdata.com.cn/",
            "enabled": True,
            "max_results": 50
        },
        "pubmed": {
            "name": "PubMed",
            "url": "https://pubmed.ncbi.nlm.nih.gov/",
            "enabled": True,
            "max_results": 50
        },
        "google_scholar": {
            "name": "Google Scholar",
            "url": "https://scholar.google.com/",
            "enabled": False,  # 需要特殊处理
            "max_results": 30
        }
    },
    "search_timeout": 10,
    "min_relevance_score": 0.3,
    "default_year_range": (2020, 2024)
}

# 模板管理配置
TEMPLATE_CONFIG = {
    "upload_dir": TEMP_DIR / "templates" / "uploaded",
    "max_upload_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": [".docx", ".pdf", ".txt", ".md"],
    "template_categories": [
        "学术论文",
        "商业报告", 
        "技术文档",
        "研究报告",
        "数据分析报告",
        "其他"
    ]
}

# 用户界面配置
UI_CONFIG = {
    "theme": "light",
    "sidebar_expanded": True,
    "show_progress": True,
    "max_displayed_rows": 1000,
    "date_format": "%Y-%m-%d",
    "number_format": "{:.3f}",
    "language": "zh-CN"
}

# 系统日志配置
LOG_CONFIG = {
    "level": "INFO",
    "file": TEMP_DIR / "system.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# 缓存配置
CACHE_CONFIG = {
    "enabled": True,
    "backend": "memory",  # memory, redis, file
    "ttl": 3600,  # 1小时
    "max_size": 100,  # 最大缓存条目数
    "cache_dir": TEMP_DIR / "cache"
}

# 安全配置
SECURITY_CONFIG = {
    "max_upload_size": 100 * 1024 * 1024,  # 100MB
    "allowed_file_types": [".csv", ".xlsx", ".xls", ".json", ".txt", ".docx", ".pdf"],
    "scan_uploads": True,
    "rate_limit": {
        "enabled": False,
        "requests_per_minute": 60
    }
}

# 性能配置
PERFORMANCE_CONFIG = {
    "multiprocessing": True,
    "max_workers": 4,
    "chunk_size": 10000,
    "memory_limit": 2 * 1024 * 1024 * 1024,  # 2GB
    "optimize_memory": True
}

# 导出所有配置
CONFIG = {
    "app": APP_CONFIG,
    "ai": AI_CONFIG,
    "analysis": ANALYSIS_CONFIG,
    "spss": SPSS_CONFIG,
    "visualization": VISUALIZATION_CONFIG,
    "report": REPORT_CONFIG,
    "literature": LITERATURE_CONFIG,
    "template": TEMPLATE_CONFIG,
    "ui": UI_CONFIG,
    "log": LOG_CONFIG,
    "cache": CACHE_CONFIG,
    "security": SECURITY_CONFIG,
    "performance": PERFORMANCE_CONFIG
}

def get_config(section: str = None):
    """获取配置"""
    if section:
        return CONFIG.get(section, {})
    return CONFIG

def update_config(section: str, key: str, value):
    """更新配置"""
    if section in CONFIG:
        CONFIG[section][key] = value
        return True
    return False