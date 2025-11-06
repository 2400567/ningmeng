#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理模块初始化文件
"""

from .template_manager import (
    AnalysisTemplate,
    TemplateManager,
    create_template_manager,
    render_template_upload_ui,
    PREDEFINED_TEMPLATES
)

__all__ = [
    'AnalysisTemplate',
    'TemplateManager', 
    'create_template_manager',
    'render_template_upload_ui',
    'PREDEFINED_TEMPLATES'
]