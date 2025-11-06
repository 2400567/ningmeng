#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果展示模块初始化文件
"""

from .spssau_renderer import (
    SPSSAUResultRenderer,
    create_spssau_renderer,
    render_analysis_results
)

__all__ = [
    'SPSSAUResultRenderer',
    'create_spssau_renderer', 
    'render_analysis_results'
]