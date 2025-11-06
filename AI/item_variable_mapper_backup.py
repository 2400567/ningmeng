#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题项变量映射系统
基于Cronbach信度分析结果创建题项到变量的映射关系
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Optional
import re

class ItemVariableMapper:
    """题项变量映射器"""
    
    def __init__(self):
        """初始化映射器"""
        self.construct_items = {
            '绩效期望': ['Q1', 'Q2', 'Q3', 'Q4'],
            '努力期望': ['Q5', 'Q6', 'Q7', 'Q8'],
            '社会影响': ['Q9', 'Q10', 'Q11', 'Q12'],
            '促进条件': ['Q13', 'Q14', 'Q15', 'Q16'],
            '享乐动机': ['Q17', 'Q18', 'Q19'],
            '价值认知': ['Q20', 'Q21', 'Q22'],
            '技术信任': ['Q23', 'Q24', 'Q25'],
            '感知风险': ['Q26', 'Q27'],
            '个体创新': ['Q28', 'Q29', 'Q30'],
            '消费意愿': ['Q31', 'Q32', 'Q33', 'Q34'],
            '消费行为': ['Q35', 'Q36', 'Q37']
        }
        
        self.cronbach_alpha = {
            '绩效期望': 0.817,
            '努力期望': 0.750,
            '社会影响': 0.676,
            '促进条件': 0.785,
            '享乐动机': 0.773,
            '价值认知': 0.767,
            '技术信任': 0.778,
            '感知风险': 0.689,
            '个体创新': 0.747,
            '消费意愿': 0.817,
            '消费行为': 0.822
        }
    
    def create_variable_mapping(self, data_columns: List[str]) -> Dict[str, str]:
        """
        创建从数据列名到变量名的映射
        
        Args:
            data_columns: 数据文件的列名列表
            
        Returns:
            映射字典 {数据列名: 变量名}
        """
        mapping = {}
        
        for construct, items in self.construct_items.items():
            for item in items:
                # 查找包含该题项的数据列
                matching_columns = self._find_matching_columns(item, data_columns)
                
                for col in matching_columns:
                    # 创建变量名：构念_题项
                    variable_name = f"{construct}_{item}"
                    mapping[col] = variable_name
        
        return mapping
    
    def create_multi_mapping_suggestions(self, data_columns: List[str]) -> Dict[str, List[str]]:
        """
        创建多选映射建议
        为每个数据列提供多个可能的映射选项
        
        Args:
            data_columns: 数据文件的列名列表
            
        Returns:
            映射建议字典 {数据列名: [可能的变量名列表]}
        """
        suggestions = {}
        
        for col in data_columns:
            possible_mappings = []
            
            # 对每个构念的每个题项进行匹配
            for construct, items in self.construct_items.items():
                for item in items:
                    # 检查是否匹配
                    if self._is_column_match(col, item):
                        variable_name = f"{construct}_{item}"
                        possible_mappings.append(variable_name)
            
            # 如果有匹配，添加到建议中
            if possible_mappings:
                suggestions[col] = possible_mappings
        
        return suggestions
    
    def _is_column_match(self, column: str, item: str) -> bool:
        """判断列名是否与题项匹配"""
        # 精确匹配
        if item in column:
            return True
        
        # 提取题项编号进行匹配
        item_num = re.search(r'\d+', item)
        if item_num:
            num = item_num.group()
            if f"Q{num}" in column or f"q{num}" in column:
                return True
        
        return False
    
    def _find_matching_columns(self, item: str, columns: List[str]) -> List[str]:
        """查找匹配的数据列"""
        matches = []
        
        # 精确匹配
        for col in columns:
            if item in col:
                matches.append(col)
        
        # 如果没有精确匹配，尝试模糊匹配
        if not matches:
            item_num = re.search(r'\d+', item)
            if item_num:
                num = item_num.group()
                for col in columns:
                    if f"Q{num}" in col or f"q{num}" in col:
                        matches.append(col)
        
        return matches
    
    def apply_variable_mapping(self, df: pd.DataFrame, mapping: Dict[str, str], multi_select_mappings: Optional[Dict[str, List[str]]] = None) -> pd.DataFrame:
        """
        应用变量映射到数据框，支持多选映射
        
        Args:
            df: 原始数据框
            mapping: 列名映射字典
            multi_select_mappings: 多选映射信息
            
        Returns:
            重命名后的数据框
        """
        df_result = df.copy()
        
        if multi_select_mappings:
            # 处理多选映射
            for original_col, selected_mappings in multi_select_mappings.items():
                if original_col in df_result.columns and len(selected_mappings) > 1:
                    # 为多选映射创建副本列
                    for i, mapping_target in enumerate(selected_mappings):
                        if i == 0:
                            # 第一个映射：重命名原列
                            df_result = df_result.rename(columns={original_col: mapping_target})
                        else:
                            # 其他映射：创建副本列
                            df_result[mapping_target] = df[original_col].copy()
        
        # 应用剩余的单选映射
        rename_dict = {}
        for old_col, new_var in mapping.items():
            if old_col in df_result.columns:
                # 检查是否已经在多选映射中处理过
                if multi_select_mappings and old_col in multi_select_mappings:
                    continue
                rename_dict[old_col] = new_var
        
        if rename_dict:
            df_result = df_result.rename(columns=rename_dict)
        
        return df_result
    
    def get_construct_variables(self, construct: str) -> List[str]:
        """获取某个构念的所有变量"""
        if construct in self.construct_items:
            items = self.construct_items[construct]
            return [f"{construct}_{item}" for item in items]
        return []
    
    def validate_construct_reliability(self, construct: str) -> Tuple[bool, float]:
        """
        验证构念的信度
        
        Returns:
            (是否可靠, Cronbach α值)
        """
        alpha = self.cronbach_alpha.get(construct, 0.0)
        is_reliable = alpha >= 0.7  # 通常认为α≥0.7表示内部一致性良好
        
        return is_reliable, alpha
    
    def render_mapping_interface(self, data_columns: List[str]) -> Optional[Dict[str, str]]:
        """渲染题项变量映射界面"""
        st.subheader("🔄 题项变量映射")
        
        st.info("""
        **基于Cronbach信度分析的题项映射**
        
        系统将根据您的信度分析结果，自动创建题项到变量的映射关系。
        支持多选映射，一个题项可以映射到多个构念。
        """)
        
        # 显示构念信息
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 构念信度统计**")
            reliability_df = pd.DataFrame([
                {
                    '构念': construct,
                    'Cronbach α': alpha,
                    '题项数量': len(items),
                    '信度等级': '良好' if alpha >= 0.8 else '可接受' if alpha >= 0.7 else '需改进'
                }
                for construct, alpha in self.cronbach_alpha.items()
                for items in [self.construct_items[construct]]
            ])
            st.dataframe(reliability_df, use_container_width=True)
        
        with col2:
            st.write("**🎯 题项分布**")
            total_items = sum(len(items) for items in self.construct_items.values())
            reliable_constructs = sum(1 for alpha in self.cronbach_alpha.values() if alpha >= 0.7)
            
            st.metric("总题项数", total_items)
            st.metric("可靠构念数", f"{reliable_constructs}/{len(self.cronbach_alpha)}")
            st.metric("平均信度", f"{sum(self.cronbach_alpha.values())/len(self.cronbach_alpha):.3f}")
        
        # 映射模式选择
        st.markdown("---")
        mapping_mode = st.radio(
            "选择映射模式",
            ["自动映射", "手动多选映射"],
            horizontal=True,
            help="自动映射：系统自动创建一对一映射；手动多选映射：为每个题项手动选择多个映射目标"
        )
        
        if mapping_mode == "自动映射":
            return self._render_auto_mapping(data_columns)
        else:
            return self._render_multi_select_mapping(data_columns)
    
    def _render_auto_mapping(self, data_columns: List[str]) -> Optional[Dict[str, str]]:
        """渲染自动映射界面"""
        if st.button("🚀 创建自动题项映射", type="primary"):
            mapping = self.create_variable_mapping(data_columns)
            
            if mapping:
                st.success(f"✅ 成功创建 {len(mapping)} 个题项变量映射")
                
                # 显示映射结果
                st.write("**📋 映射结果预览**")
                mapping_df = pd.DataFrame([
                    {'数据列名': col, '变量名': var, '所属构念': var.split('_')[0]}
                    for col, var in mapping.items()
                ])
                st.dataframe(mapping_df, use_container_width=True)
                
                # 保存到session state
                st.session_state['item_variable_mapping'] = mapping
                st.session_state['construct_variables'] = {
                    construct: self.get_construct_variables(construct)
                    for construct in self.construct_items.keys()
                }
                
                return mapping
            else:
                st.warning("⚠️ 未找到匹配的题项，请检查数据列名格式")
        
        return None
    
    def _render_multi_select_mapping(self, data_columns: List[str]) -> Optional[Dict[str, str]]:
        """渲染多选映射界面"""
        st.write("**🎯 手动多选映射**")
        st.info("为每个数据列选择一个或多个映射目标。支持一个题项映射到多个构念。")
        
        # 获取映射建议
        suggestions = self.create_multi_mapping_suggestions(data_columns)
        
        # 过滤出可能是题项的列
        question_columns = [col for col in data_columns if any(pattern in col.upper() for pattern in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9'])]
        
        if not question_columns:
            st.warning("⚠️ 未检测到题项格式的列名，请确保列名包含Q1, Q2等标识")
            return None
        
        st.write(f"检测到 **{len(question_columns)}** 个可能的题项列")
        
        # 创建映射选择界面
        mapping_selections = {}
        
        for i, col in enumerate(question_columns):
            with st.expander(f"📝 {col[:60]}{'...' if len(col) > 60 else ''}", expanded=i < 5):
                st.write(f"**数据列**: `{col}`")
                
                # 获取建议的映射选项
                if col in suggestions:
                    suggested_options = suggestions[col]
                    st.write(f"**系统建议** ({len(suggested_options)} 个选项):")
                    
                    # 多选框
                    selected_mappings = st.multiselect(
                        "选择映射目标",
                        options=suggested_options,
                        default=suggested_options[:1],  # 默认选择第一个建议
                        key=f"multi_mapping_{i}",
                        help="可以选择多个映射目标，题项将被复制到多个构念中"
                    )
                    
                    if selected_mappings:
                        mapping_selections[col] = selected_mappings
                        st.success(f"✅ 已选择 {len(selected_mappings)} 个映射: {', '.join(selected_mappings)}")
                else:
                    st.write("❌ 未找到自动映射建议")
                    
                    # 手动选择所有可能的变量
                    all_variables = []
                    for construct, items in self.construct_items.items():
                        for item in items:
                            all_variables.append(f"{construct}_{item}")
                    
                    manual_selections = st.multiselect(
                        "手动选择映射目标",
                        options=all_variables,
                        key=f"manual_mapping_{i}",
                        help="从所有可能的变量中手动选择"
                    )
                    
                    if manual_selections:
                        mapping_selections[col] = manual_selections
        
        # 显示映射摘要
        if mapping_selections:
            st.markdown("---")
            st.write("**📊 映射摘要**")
            
            total_mappings = sum(len(mappings) for mappings in mapping_selections.values())
            st.metric("总映射数", f"{total_mappings} 个")
            
            # 按构念显示映射统计
            construct_counts = {}
            for col, mappings in mapping_selections.items():
                for mapping in mappings:
                    construct = mapping.split('_')[0]
                    if construct not in construct_counts:
                        construct_counts[construct] = 0
                    construct_counts[construct] += 1
            
            if construct_counts:
                st.write("**各构念映射数量**:")
                for construct, count in sorted(construct_counts.items()):
                    alpha = self.cronbach_alpha.get(construct, 0.0)
                    reliability_status = "🟢" if alpha >= 0.8 else "🟡" if alpha >= 0.7 else "🔴"
                    st.write(f"- {reliability_status} {construct}: {count} 个映射 (α={alpha:.3f})")
            
            # 应用多选映射
            if st.button("✅ 应用多选映射", type="primary"):
                # 创建最终映射字典（展开多选）
                final_mapping = {}
                
                for col, mappings in mapping_selections.items():
                    if len(mappings) == 1:
                        # 单选映射
                        final_mapping[col] = mappings[0]
                    else:
                        # 多选映射：为每个映射创建新列名
                        for i, mapping in enumerate(mappings):
                            if i == 0:
                                final_mapping[col] = mapping
                            else:
                                # 创建副本列名
                                new_col_name = f"{col}_副本{i}"
                                final_mapping[new_col_name] = mapping
                
                st.session_state['item_variable_mapping'] = final_mapping
                st.session_state['multi_select_mappings'] = mapping_selections
                st.session_state['construct_variables'] = {
                    construct: self.get_construct_variables(construct)
                    for construct in self.construct_items.keys()
                }
                
                st.success(f"✅ 多选映射已保存！共创建 {len(final_mapping)} 个映射关系")
                
                # 显示最终映射预览
                with st.expander("📋 最终映射预览"):
                    final_df = pd.DataFrame([
                        {'原列名': col, '新变量名': var, '构念': var.split('_')[0]}
                        for col, var in final_mapping.items()
                    ])
                    st.dataframe(final_df, use_container_width=True)
                
                return final_mapping
        
        return None
                st.dataframe(mapping_df, use_container_width=True)
                
                # 保存到session state
                st.session_state['item_variable_mapping'] = mapping
                st.session_state['construct_variables'] = {
                    construct: self.get_construct_variables(construct)
                    for construct in self.construct_items.keys()
                }
                
                return mapping
            else:
                st.warning("⚠️ 未找到匹配的题项，请检查数据列名格式")
        
        return None
    
    def render_construct_analysis_options(self):
        """渲染构念分析选项"""
        st.subheader("📈 构念分析选项")
        
        # 选择要分析的构念
        selected_constructs = st.multiselect(
            "选择要分析的构念",
            options=list(self.construct_items.keys()),
            default=list(self.construct_items.keys()),
            help="选择您想要进行深入分析的构念"
        )
        
        if selected_constructs:
            # 分析类型选择
            analysis_types = st.multiselect(
                "选择分析类型",
                options=[
                    "描述性统计",
                    "相关性分析", 
                    "因子分析",
                    "结构方程模型",
                    "回归分析",
                    "聚类分析"
                ],
                default=["描述性统计", "相关性分析"],
                help="选择要执行的分析方法"
            )
            
            # 保存分析配置
            if st.button("💾 保存分析配置"):
                st.session_state['selected_constructs'] = selected_constructs
                st.session_state['selected_analysis_types'] = analysis_types
                
                st.success("✅ 分析配置已保存")
                
                # 显示配置摘要
                st.write("**📋 配置摘要**")
                config_summary = pd.DataFrame([
                    {
                        '构念': construct,
                        '题项': ', '.join(self.construct_items[construct]),
                        'Cronbach α': self.cronbach_alpha[construct],
                        '变量数': len(self.construct_items[construct])
                    }
                    for construct in selected_constructs
                ])
                st.dataframe(config_summary, use_container_width=True)


def create_item_mapping_interface():
    """创建题项映射界面的主函数"""
    mapper = ItemVariableMapper()
    
    st.title("🎯 题项变量映射系统")
    
    # 检查是否有数据
    if 'uploaded_data' not in st.session_state:
        st.warning("⚠️ 请先上传数据文件")
        return None
    
    data = st.session_state['uploaded_data']
    data_columns = list(data.columns)
    
    # 渲染映射界面
    mapping = mapper.render_mapping_interface(data_columns)
    
    # 渲染分析选项
    mapper.render_construct_analysis_options()
    
    return mapping


if __name__ == "__main__":
    # 测试代码
    mapper = ItemVariableMapper()
    
    # 模拟数据列
    test_columns = [
        'Q1_我认为AI虚拟主播能提高购物效率',
        'Q2_AI虚拟主播让我更快找到想要的商品',
        'Q3_使用AI虚拟主播购物对我很有用',
        'Q4_AI虚拟主播提高了我的购物体验质量'
    ]
    
    mapping = mapper.create_variable_mapping(test_columns)
    print("映射结果:", mapping)