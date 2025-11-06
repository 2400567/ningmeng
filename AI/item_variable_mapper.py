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
    
    def apply_variable_mapping(self, df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """
        应用变量映射到数据框
        
        Args:
            df: 原始数据框
            mapping: 列名映射字典
            
        Returns:
            重命名后的数据框
        """
        # 创建重命名字典
        rename_dict = {}
        for old_col, new_var in mapping.items():
            if old_col in df.columns:
                rename_dict[old_col] = new_var
        
        # 应用重命名
        df_renamed = df.rename(columns=rename_dict)
        
        return df_renamed
    
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
        每个构念的题项将被映射为对应的分析变量。
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
        
        # 创建映射
        if st.button("🚀 创建题项变量映射", type="primary"):
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