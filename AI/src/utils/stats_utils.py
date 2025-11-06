#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计辅助工具

提供统一的 p 值清洗与格式化函数，避免在渲染或显著性判断时因类型不一致
(字符串 / None / '<0.001' / 'NA' 等) 引发异常或比较错误。

设计原则:
1. 清洗: 任意输入 -> float 或 np.nan
2. 显示: 标准化字符串 ("<0.001" 或 3位小数)
3. 显著性: 依据数值阈值计算标记 ** / * / ''
4. 安全: 出错时回退 np.nan
"""
from __future__ import annotations
import re
import math
from typing import Any, Tuple
import numpy as np

_P_LT_PATTERN = re.compile(r"^<\s*([0-9]*\.?[0-9]+)")
_NUM_PATTERN = re.compile(r"^[+-]?([0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?)$")

_EMPTY_MARKERS = {"", "na", "nan", "none", "null", "--", "n/a"}

def clean_p_value(value: Any) -> float:
    """将任意形式的 p 值输入转换为 float; 无法解析返回 np.nan.

    支持情形:
    - 数值 (int/float)
    - 字符串: '0.05', '0.05 ', '<0.001', '< .05', '1e-5'
    - 空或占位: '', 'NA', None -> np.nan
    - 其它不可解析 -> np.nan
    """
    if value is None:
        return float('nan')

    # 直接数值
    if isinstance(value, (int, float)):
        v = float(value)
        # 负值或 >1 视为异常，转 nan
        if v < 0 or v > 1.5:
            return float('nan')
        return v

    # 字符串处理
    if isinstance(value, str):
        s = value.strip()
        if s.lower() in _EMPTY_MARKERS:
            return float('nan')
        # 处理形如 '<0.05'
        m = _P_LT_PATTERN.match(s.replace(' ', ''))
        if m:
            try:
                base = float(m.group(1))
                # 保守估计：取一半或最小 1e-6
                return max(base / 2.0, 1e-6)
            except Exception:
                return float('nan')
        # 普通数值
        if _NUM_PATTERN.match(s):
            try:
                v = float(s)
                if v < 0 or v > 1.5:
                    return float('nan')
                return v
            except Exception:
                return float('nan')
        # 提取嵌入数字 (如 'p=0.034')
        nums = re.findall(r"[0-9]*\.?[0-9]+", s)
        if nums:
            try:
                v = float(nums[0])
                if 0 <= v <= 1.5:
                    return v
            except Exception:
                pass
    return float('nan')

def format_p_value(p: float) -> str:
    """格式化 p 值显示字符串.
    - nan -> '' (留空)
    - <0.001 -> '<0.001'
    - else 3位小数
    """
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return ''
    if p < 0.001:
        return '<0.001'
    return f"{p:.3f}"

def significance_marker(p: float) -> str:
    """根据数值 p 返回显著性符号."""
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return ''
    if p < 0.01:
        return '**'
    if p < 0.05:
        return '*'
    return ''

__all__ = [
    'clean_p_value', 'format_p_value', 'significance_marker'
]
