#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变量合并工具
提供问卷变量的合并、重新编码、计算功能
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class VariableMergeRule:
    """变量合并规则"""
    rule_name: str
    target_variable: str
    source_variables: List[str]
    merge_method: str  # 'mean', 'sum', 'weighted_mean', 'factor_score'
    weights: Optional[List[float]] = None
    reverse_items: Optional[List[str]] = None
    scale_range: Optional[Tuple[int, int]] = None
    description: str = ""

class VariableMerger:
    """变量合并器"""
    
    def __init__(self):
        self.merge_rules: Dict[str, VariableMergeRule] = {}
        self.data: Optional[pd.DataFrame] = None
        
    def set_data(self, data: pd.DataFrame):
        """设置数据"""
        self.data = data.copy()
        
    def add_merge_rule(self, rule: VariableMergeRule) -> bool:
        """添加合并规则"""
        try:
            # 验证规则
            if not self._validate_rule(rule):
                return False
            
            self.merge_rules[rule.rule_name] = rule
            return True
        except Exception as e:
            logger.error(f"添加合并规则失败: {e}")
            return False
    
    def _validate_rule(self, rule: VariableMergeRule) -> bool:
        """验证合并规则"""
        if not rule.source_variables:
            st.error("源变量列表不能为空")
            return False
        
        if self.data is not None:
            missing_vars = [var for var in rule.source_variables if var not in self.data.columns]
            if missing_vars:
                st.error(f"以下变量在数据中不存在: {', '.join(missing_vars)}")
                return False
        
        if rule.merge_method == 'weighted_mean' and (not rule.weights or len(rule.weights) != len(rule.source_variables)):
            st.error("加权平均需要为每个源变量提供权重")
            return False
        
        return True
    
    def apply_merge_rule(self, rule_name: str) -> bool:
        """应用合并规则"""
        try:
            rule = self.merge_rules.get(rule_name)
            if not rule or self.data is None:
                return False
            
            # 获取源数据
            source_data = self.data[rule.source_variables].copy()
            
            # 反向计分
            if rule.reverse_items:
                source_data = self._reverse_score(source_data, rule.reverse_items, rule.scale_range)
            
            # 应用合并方法
            if rule.merge_method == 'mean':
                merged_values = source_data.mean(axis=1)
            elif rule.merge_method == 'sum':
                merged_values = source_data.sum(axis=1)
            elif rule.merge_method == 'weighted_mean':
                merged_values = np.average(source_data, axis=1, weights=rule.weights)
            elif rule.merge_method == 'factor_score':
                merged_values = self._calculate_factor_score(source_data)
            else:
                st.error(f"不支持的合并方法: {rule.merge_method}")
                return False
            
            # 添加到数据中
            self.data[rule.target_variable] = merged_values
            
            return True
            
        except Exception as e:
            logger.error(f"应用合并规则失败: {e}")
            return False
    
    def _reverse_score(self, data: pd.DataFrame, reverse_items: List[str], scale_range: Tuple[int, int]) -> pd.DataFrame:
        """反向计分"""
        data_reversed = data.copy()
        min_val, max_val = scale_range
        
        for item in reverse_items:
            if item in data_reversed.columns:
                data_reversed[item] = (min_val + max_val) - data_reversed[item]
        
        return data_reversed
    
    def _calculate_factor_score(self, data: pd.DataFrame) -> pd.Series:
        """计算因子得分"""
        try:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler
            
            # 标准化数据
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data.dropna())
            
            # PCA提取第一主成分
            pca = PCA(n_components=1)
            factor_scores = pca.fit_transform(scaled_data)
            
            # 创建完整的Series（包含缺失值）
            result = pd.Series(index=data.index, dtype=float)
            result.loc[data.dropna().index] = factor_scores.flatten()
            
            return result
            
        except Exception as e:
            logger.error(f"计算因子得分失败: {e}")
            # 降级为平均值
            return data.mean(axis=1)
    
    def apply_all_rules(self) -> bool:
        """应用所有合并规则"""
        success_count = 0
        for rule_name in self.merge_rules:
            if self.apply_merge_rule(rule_name):
                success_count += 1
        
        return success_count == len(self.merge_rules)
    
    def get_merged_data(self) -> pd.DataFrame:
        """获取合并后的数据"""
        return self.data.copy() if self.data is not None else pd.DataFrame()
    
    def remove_rule(self, rule_name: str) -> bool:
        """移除合并规则"""
        if rule_name in self.merge_rules:
            del self.merge_rules[rule_name]
            return True
        return False
    
    def get_rule_summary(self) -> Dict[str, Any]:
        """获取规则摘要"""
        summary = {}
        for rule_name, rule in self.merge_rules.items():
            summary[rule_name] = {
                'target_variable': rule.target_variable,
                'source_count': len(rule.source_variables),
                'method': rule.merge_method,
                'description': rule.description
            }
        return summary

def render_variable_merger_ui(data: pd.DataFrame) -> Tuple[pd.DataFrame, VariableMerger]:
    """渲染变量合并界面"""
    st.header("🔧 变量合并工具")
    
    # 初始化合并器
    if 'variable_merger' not in st.session_state:
        st.session_state.variable_merger = VariableMerger()
    
    merger = st.session_state.variable_merger
    merger.set_data(data)
    
    # 创建新的合并规则
    st.subheader("创建变量合并规则")
    
    with st.form("variable_merge_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            rule_name = st.text_input("规则名称", help="为这个合并规则取一个名字")
            target_variable = st.text_input("目标变量名", help="合并后的新变量名称")
            merge_method = st.selectbox(
                "合并方法",
                ['mean', 'sum', 'weighted_mean', 'factor_score'],
                format_func=lambda x: {
                    'mean': '平均值',
                    'sum': '求和',
                    'weighted_mean': '加权平均',
                    'factor_score': '因子得分'
                }[x]
            )
        
        with col2:
            available_vars = list(data.columns)
            source_variables = st.multiselect(
                "选择源变量",
                available_vars,
                help="选择要合并的原始变量"
            )
            
            description = st.text_area("描述", help="描述这个合并规则的用途")
        
        # 高级选项
        with st.expander("高级选项"):
            col3, col4 = st.columns(2)
            
            with col3:
                # 反向计分
                st.write("**反向计分项**")
                if source_variables:
                    reverse_items = st.multiselect(
                        "需要反向计分的变量",
                        source_variables,
                        help="选择需要反向计分的变量"
                    )
                else:
                    reverse_items = []
                
                if reverse_items:
                    scale_min = st.number_input("量表最小值", value=1)
                    scale_max = st.number_input("量表最大值", value=5)
                    scale_range = (int(scale_min), int(scale_max))
                else:
                    scale_range = None
            
            with col4:
                # 权重设置
                weights = None
                if merge_method == 'weighted_mean' and source_variables:
                    st.write("**变量权重**")
                    weights = []
                    for var in source_variables:
                        weight = st.number_input(f"{var} 权重", value=1.0, min_value=0.0, step=0.1)
                        weights.append(weight)
        
        submitted = st.form_submit_button("添加合并规则", type="primary")
        
        if submitted and rule_name and target_variable and source_variables:
            rule = VariableMergeRule(
                rule_name=rule_name,
                target_variable=target_variable,
                source_variables=source_variables,
                merge_method=merge_method,
                weights=weights,
                reverse_items=reverse_items if reverse_items else None,
                scale_range=scale_range,
                description=description
            )
            
            if merger.add_merge_rule(rule):
                st.success(f"合并规则 '{rule_name}' 添加成功！")
                st.rerun()
            else:
                st.error("添加合并规则失败！")
    
    # 显示现有规则
    st.subheader("现有合并规则")
    
    if merger.merge_rules:
        for rule_name, rule in merger.merge_rules.items():
            with st.expander(f"📋 {rule_name}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**目标变量**: {rule.target_variable}")
                    st.write(f"**合并方法**: {rule.merge_method}")
                    st.write(f"**源变量**: {', '.join(rule.source_variables)}")
                    if rule.description:
                        st.write(f"**描述**: {rule.description}")
                
                with col2:
                    if st.button("应用", key=f"apply_{rule_name}"):
                        if merger.apply_merge_rule(rule_name):
                            st.success(f"规则 '{rule_name}' 应用成功！")
                            st.rerun()
                        else:
                            st.error("应用规则失败！")
                
                with col3:
                    if st.button("删除", key=f"delete_{rule_name}"):
                        if merger.remove_rule(rule_name):
                            st.success("规则删除成功！")
                            st.rerun()
        
        # 批量应用
        if st.button("应用所有规则", type="primary"):
            if merger.apply_all_rules():
                st.success("所有规则应用成功！")
                st.rerun()
            else:
                st.error("部分规则应用失败！")
    else:
        st.info("暂无合并规则，请创建新的合并规则")
    
    # 显示数据预览
    merged_data = merger.get_merged_data()
    
    if len(merged_data.columns) > len(data.columns):
        st.subheader("数据预览")
        
        # 显示新增变量
        new_variables = [col for col in merged_data.columns if col not in data.columns]
        if new_variables:
            st.write("**新增变量**:", ", ".join(new_variables))
            
            # 显示新变量的统计信息
            new_var_stats = merged_data[new_variables].describe()
            st.dataframe(new_var_stats, use_container_width=True)
        
        # 数据预览
        with st.expander("完整数据预览"):
            st.dataframe(merged_data, use_container_width=True)
    
    return merged_data, merger

# 预设合并规则模板
MERGE_RULE_TEMPLATES = {
    "UTAUT2_PE": {
        "rule_name": "绩效期望",
        "target_variable": "Performance_Expectancy",
        "source_variables": ["PE1", "PE2", "PE3", "PE4"],
        "merge_method": "mean",
        "description": "UTAUT2模型中的绩效期望构念"
    },
    
    "UTAUT2_EE": {
        "rule_name": "努力期望", 
        "target_variable": "Effort_Expectancy",
        "source_variables": ["EE1", "EE2", "EE3", "EE4"],
        "merge_method": "mean",
        "description": "UTAUT2模型中的努力期望构念"
    },
    
    "UTAUT2_SI": {
        "rule_name": "社会影响",
        "target_variable": "Social_Influence", 
        "source_variables": ["SI1", "SI2", "SI3"],
        "merge_method": "mean",
        "description": "UTAUT2模型中的社会影响构念"
    },
    
    "UTAUT2_FC": {
        "rule_name": "便利条件",
        "target_variable": "Facilitating_Conditions",
        "source_variables": ["FC1", "FC2", "FC3", "FC4"],
        "merge_method": "mean", 
        "description": "UTAUT2模型中的便利条件构念"
    }
}

def create_variable_merger() -> VariableMerger:
    """创建变量合并器实例"""
    return VariableMerger()

def render_variable_merger_ui(merger: VariableMerger, data: pd.DataFrame) -> pd.DataFrame:
    """渲染变量合并界面（简化版本）"""
    st.subheader("🔗 变量合并工具")
    
    if data is None or data.empty:
        st.warning("请先上传数据")
        return None
    
    merger.set_data(data)
    
    # 创建合并规则
    with st.expander("➕ 创建新的合并规则", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            target_var = st.text_input("目标变量名", placeholder="例: PU")
            method = st.selectbox("合并方法", ["mean", "sum", "weighted_mean", "factor_score"])
        
        with col2:
            available_vars = list(data.columns)
            source_vars = st.multiselect("选择源变量", available_vars)
            
            if method == "weighted_mean":
                weights = st.text_input("权重（逗号分隔）", placeholder="例: 0.3,0.4,0.3")
            else:
                weights = None
        
        # 反向计分设置
        reverse_vars = st.multiselect("需要反向计分的变量", source_vars)
        scale_range = (1, 5)  # 默认量表范围
        
        if st.button("🔄 应用合并规则"):
            if target_var and source_vars:
                try:
                    # 创建合并规则
                    rule = VariableMergeRule(
                        rule_name=f"rule_{target_var}",
                        target_variable=target_var,
                        source_variables=source_vars,
                        merge_method=method,
                        weights=[float(w.strip()) for w in weights.split(",")] if weights else None,
                        reverse_items=reverse_vars if reverse_vars else None,
                        scale_range=scale_range
                    )
                    
                    # 添加并应用合并规则
                    if merger.add_merge_rule(rule) and merger.apply_merge_rule(rule.rule_name):
                        merged_data = merger.get_merged_data()
                        
                        st.success(f"变量 {target_var} 合并成功！")
                        
                        # 显示结果预览
                        st.write("**合并结果预览:**")
                        preview_cols = source_vars + [target_var]
                        st.dataframe(merged_data[preview_cols].head())
                        
                        return merged_data
                    else:
                        st.error("合并失败")
                        
                except Exception as e:
                    st.error(f"合并失败: {e}")
            else:
                st.error("请填写目标变量名和选择源变量")
    
    return data