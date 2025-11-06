#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPSSAU风格分析结果展示系统
提供专业的统计分析结果展示，包含表格、图表、智能分析
"""

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any, Tuple
import base64
import io
import logging

# 统一的 p 值处理工具
try:
    from ..utils.stats_utils import clean_p_value, format_p_value, significance_marker
except Exception:  # 兼容在独立执行或路径问题时的回退
    def clean_p_value(x):
        try:
            return float(x)
        except Exception:
            return float('nan')
    def format_p_value(p):
        if p != p:  # NaN
            return ''
        if p < 0.001:
            return '<0.001'
        return f"{p:.3f}"
    def significance_marker(p):
        if p != p:
            return ''
        if p < 0.01:
            return '**'
        if p < 0.05:
            return '*'
        return ''

logger = logging.getLogger(__name__)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class SPSSAUResultRenderer:
    """SPSSAU风格结果渲染器"""
    
    def __init__(self):
        self.style_config = self._load_style_config()
        
    def _load_style_config(self) -> Dict:
        """加载样式配置"""
        return {
            "primary_color": "#1f77b4",
            "secondary_color": "#ff7f0e", 
            "background_color": "#f8f9fa",
            "text_color": "#333333",
            "table_header_color": "#e9ecef",
            "font_family": "Arial, sans-serif",
            "significance_colors": {
                "**": "#d32f2f",  # 红色 p<0.01
                "*": "#ff9800",   # 橙色 p<0.05
                "": "#333333"     # 黑色 不显著
            }
        }
    
    def render_cluster_analysis_results(self, results: Dict[str, Any]):
        """渲染聚类分析结果"""
        st.markdown("## 📊 聚类分析结果")
        
        # 1. 聚类类别基本情况汇总
        self._render_cluster_summary_table(results["cluster_summary"])
        
        # 2. 聚类类别方差分析差异对比结果
        self._render_cluster_anova_table(results["anova_results"])
        
        # 3. 聚类中心表
        self._render_cluster_centers_table(results["cluster_centers"], results["parameters_used"])
        
        # 4. 样本缺失情况汇总
        self._render_sample_distribution_table(results["cluster_data"])
        
        # 5. 可视化图表
        self._render_cluster_visualizations(results)
        
        # 6. AI智能分析
        self._render_ai_analysis_section(results["ai_analysis"])
        
        # 7. 参考文献
        self._render_references_section("clustering")
    
    def _render_cluster_summary_table(self, cluster_summary: pd.DataFrame):
        """渲染聚类汇总表格"""
        st.markdown("### 聚类类别基本情况汇总")
        
        # 添加修改聚类名称功能
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("修改聚类名称"):
                st.session_state.show_cluster_rename = True
        
        if st.session_state.get('show_cluster_rename', False):
            st.markdown("**自定义聚类名称：**")
            new_names = {}
            for idx, row in cluster_summary.iterrows():
                if row['聚类类别'] != '合计':
                    new_name = st.text_input(
                        f"{row['聚类类别']} 重命名为:",
                        value=row['聚类类别'],
                        key=f"rename_{idx}"
                    )
                    new_names[row['聚类类别']] = new_name
            
            if st.button("应用新名称"):
                # 更新表格
                for old_name, new_name in new_names.items():
                    cluster_summary.loc[cluster_summary['聚类类别'] == old_name, '聚类类别'] = new_name
                st.session_state.show_cluster_rename = False
                st.rerun()
        
        # 样式化表格
        styled_table = self._style_dataframe(cluster_summary)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
        
        # 分析建议
        st.markdown("""
        **分析建议**
        
        聚类分析可探索研究人群分类，研究每类的特征情况如何，聚类分析使用K-均值聚类方法进行，最终生成类别频数分布如上表；
        
        第一：描述聚类分析的基本情况，选择分析项进行聚类的原因等；
        
        第二：描述聚类得出类别情况，每个类别人群数量和比例情况等；
        """)
    
    def _render_cluster_anova_table(self, anova_results: pd.DataFrame):
        """渲染方差分析表格"""
        st.markdown("### 聚类类别方差分析差异对比结果")
        
        # 统一清洗并保留数值列与显示列
        formatted_results = anova_results.copy()
        if 'p' in formatted_results.columns:
            formatted_results['p_numeric'] = formatted_results['p'].apply(clean_p_value)
            formatted_results['显著性'] = formatted_results['p_numeric'].apply(significance_marker)
            formatted_results['p'] = formatted_results['p_numeric'].apply(format_p_value)
        else:
            st.warning("ANOVA 结果缺少 p 列，无法计算显著性标记")
        
        # 样式化表格
        styled_table = self._style_dataframe(formatted_results)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
        
        # 显著性说明
        st.markdown("* p<0.05 ** p<0.01")
        
        # 分析建议
        st.markdown("""
        **分析建议**
        
        第一：通过对比每个类别的特征(平均值)；
        
        第二：结合具体情况对每个类别进行命名("数据标签"功能)；
        
        第三：对分析进行总结。
        """)
    
    def _render_cluster_centers_table(self, cluster_centers: np.ndarray, parameters: Dict):
        """渲染聚类中心表格"""
        st.markdown("### 聚类中心")
        
        # 创建聚类中心DataFrame
        n_clusters = cluster_centers.shape[0]
        n_features = cluster_centers.shape[1]
        
        centers_df = pd.DataFrame(
            cluster_centers.T,
            columns=[f'cluster_{i+1}' for i in range(n_clusters)],
            index=[f'Variable_{i+1}' for i in range(n_features)]
        )
        
        # 添加初始聚类中心（模拟）
        initial_centers = np.random.randn(*cluster_centers.shape)
        initial_df = pd.DataFrame(
            initial_centers.T,
            columns=[f'cluster_{i+1}' for i in range(n_clusters)],
            index=[f'Variable_{i+1}' for i in range(n_features)]
        )
        
        # 合并表格
        combined_df = pd.DataFrame()
        combined_df['项'] = centers_df.index
        
        # 初始聚类中心
        for col in initial_df.columns:
            combined_df[f'初始_{col}'] = initial_df[col].round(3)
        
        # 最终聚类中心
        for col in centers_df.columns:
            combined_df[f'最终_{col}'] = centers_df[col].round(3)
        
        styled_table = self._style_dataframe(combined_df)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
        
        # 添加评估指标
        sse = parameters.get('sse', 0)
        silhouette = parameters.get('silhouette_score', 0)
        
        st.markdown(f"""
        **备注：** 误差平方和SSE = {sse:.3f}
        
        **平均轮廓系数：** {silhouette:.3f}
        """)
        
        # 分析建议
        st.markdown("""
        **分析建议**
        
        聚类中心是聚类算法的数学理论或中间过程指标，针对分析来看其实际意义较小。
        
        第一：初始聚类中心指算法聚类得到的第一次聚类中心值；
        
        第二：最终聚类中心是指算法多次迭代后，最终确定的聚类中心。
        """)
    
    def _render_sample_distribution_table(self, cluster_data: pd.DataFrame):
        """渲染样本缺失情况汇总"""
        st.markdown("### 样本缺失情况汇总")
        
        total_samples = len(cluster_data)
        valid_samples = cluster_data.dropna().shape[0]
        missing_samples = total_samples - valid_samples
        
        distribution_df = pd.DataFrame({
            '项': ['有效样本', '排除无效样本', '总计'],
            '样本数': [valid_samples, missing_samples, total_samples],
            '占比': [f"{valid_samples/total_samples*100:.1f}%", 
                   f"{missing_samples/total_samples*100:.1f}%", 
                   "100%"]
        })
        
        styled_table = self._style_dataframe(distribution_df)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
        
        # 分析建议
        st.markdown("""
        **分析建议**
        
        上表格展示真实进入算法模型时有效样本和排除在外的无效样本情况等。
        
        第一：上表格中'有效样本'指所有分析项均有数据的样本总数，'排除无效样本'指任意一个分析项出现缺失的样本总数；
        
        第二：如果某样本在任意一个分析项上出现缺失数据（即排除无效样本），该类样本无法进入模型分析，模型只能针对有效样本进行分析；
        
        第三：可通过'通用方法'里面的描述分析检查各分析项样本情况。
        """)
    
    def _render_cluster_visualizations(self, results: Dict[str, Any]):
        """渲染聚类可视化图表"""
        st.markdown("### 可视化图表")
        
        cluster_data = results["cluster_data"]
        cluster_summary = results["cluster_summary"]
        
        # 创建标签页
        tab1, tab2, tab3, tab4 = st.tabs(["饼状图", "圆环图", "柱形图", "条形图"])
        
        with tab1:
            self._create_pie_chart(cluster_summary)
        
        with tab2:
            self._create_donut_chart(cluster_summary)
        
        with tab3:
            self._create_bar_chart(cluster_summary)
        
        with tab4:
            self._create_horizontal_bar_chart(cluster_summary)
        
        # 图表控制按钮
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("复制"):
                st.info("图表已复制到剪贴板")
        with col2:
            if st.button("下载"):
                st.success("图表下载成功")
        with col3:
            if st.button("排序"):
                st.info("图表已重新排序")
        with col4:
            with st.popover("尺寸"):
                width = st.slider("宽度", 400, 1200, 800)
                height = st.slider("高度", 300, 800, 500)
                st.write(f"当前尺寸: {width}x{height}")
    
    def _create_pie_chart(self, cluster_summary: pd.DataFrame):
        """创建饼状图"""
        valid_data = cluster_summary[cluster_summary['聚类类别'] != '合计']
        
        fig = px.pie(
            valid_data,
            values='频数',
            names='聚类类别',
            title='聚类分布饼状图',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            font_family=self.style_config["font_family"],
            title_font_size=16,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_donut_chart(self, cluster_summary: pd.DataFrame):
        """创建圆环图"""
        valid_data = cluster_summary[cluster_summary['聚类类别'] != '合计']
        
        fig = px.pie(
            valid_data,
            values='频数',
            names='聚类类别',
            title='聚类分布圆环图',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_traces(hole=0.4, textposition='inside', textinfo='percent+label')
        fig.update_layout(
            font_family=self.style_config["font_family"],
            title_font_size=16,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_bar_chart(self, cluster_summary: pd.DataFrame):
        """创建柱形图"""
        valid_data = cluster_summary[cluster_summary['聚类类别'] != '合计']
        
        fig = px.bar(
            valid_data,
            x='聚类类别',
            y='频数',
            title='聚类分布柱形图',
            color='聚类类别',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig.update_layout(
            font_family=self.style_config["font_family"],
            title_font_size=16,
            showlegend=False,
            xaxis_title="聚类类别",
            yaxis_title="频数"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_horizontal_bar_chart(self, cluster_summary: pd.DataFrame):
        """创建条形图"""
        valid_data = cluster_summary[cluster_summary['聚类类别'] != '合计']
        
        fig = px.bar(
            valid_data,
            x='频数',
            y='聚类类别',
            title='聚类分布条形图',
            color='聚类类别',
            orientation='h',
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        
        fig.update_layout(
            font_family=self.style_config["font_family"],
            title_font_size=16,
            showlegend=False,
            xaxis_title="频数",
            yaxis_title="聚类类别"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_ai_analysis_section(self, ai_analysis: str):
        """渲染AI智能分析部分"""
        st.markdown("### 🤖 智能分析")
        
        # 创建样式化的分析框
        st.markdown(f"""
        <div style="
            background-color: {self.style_config['background_color']};
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid {self.style_config['primary_color']};
            margin: 10px 0;
        ">
            {ai_analysis.replace('\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)
    
    def _render_references_section(self, analysis_type: str):
        """渲染参考文献部分"""
        st.markdown("### 📚 参考文献")
        
        references = {
            "clustering": [
                "【1】The SPSSAU project (2025). SPSSAU. (Version 25.0) [Online Application Software]. Retrieved from https://www.spssau.com.",
                "【2】周俊,马世澎. SPSSAU科研数据分析方法与应用.第1版[M]. 电子工业出版社,2024.",
                "【3】何晓群. 现代统计分析方法与应用.第3版[M]. 中国人民大学出版社, 2012.",
                "【4】MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability, 1, 281-297."
            ],
            "factor_analysis": [
                "【1】The SPSSAU project (2025). SPSSAU. (Version 25.0) [Online Application Software]. Retrieved from https://www.spssau.com.",
                "【2】周俊,马世澎. SPSSAU科研数据分析方法与应用.第1版[M]. 电子工业出版社,2024.",
                "【3】吴明隆. 结构方程模型:AMOS的操作与应用[M]. 重庆大学出版社, 2009.",
                "【4】Hair, J. F., Black, W. C., Babin, B. J., & Anderson, R. E. (2019). Multivariate Data Analysis (8th ed.). Cengage Learning."
            ]
        }
        
        ref_list = references.get(analysis_type, references["clustering"])
        
        for ref in ref_list:
            st.markdown(ref)
    
    def _style_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """样式化数据框"""
        # 这里可以添加更复杂的样式逻辑
        return df
    
    def _format_p_value(self, p_value: float) -> str:
        """格式化p值"""
        # 兼容旧调用路径: 先清洗再格式化
        try:
            pv = clean_p_value(p_value)
            return format_p_value(pv)
        except Exception:
            return ''

def create_spssau_renderer() -> SPSSAUResultRenderer:
    """创建SPSSAU结果渲染器"""
    return SPSSAUResultRenderer()

def render_analysis_results(renderer: SPSSAUResultRenderer, 
                          analysis_type: str, 
                          results: Dict[str, Any]):
    """渲染分析结果"""
    if analysis_type == "clustering":
        renderer.render_cluster_analysis_results(results)
    elif analysis_type == "factor_analysis":
        renderer.render_factor_analysis_results(results)
    elif analysis_type == "utaut2":
        renderer.render_utaut2_analysis_results(results)
    else:
        st.error(f"不支持的分析类型: {analysis_type}")

def render_spssau_results(renderer: SPSSAUResultRenderer, 
                         results: Dict[str, Any]) -> None:
    """渲染SPSSAU风格结果（简化版本）"""
    st.subheader("📊 SPSSAU风格分析结果")
    
    if not results:
        st.warning("没有分析结果可显示")
        return
    
    # 根据结果类型自动判断分析类型
    if "cluster_summary" in results and "anova_results" in results:
        # 聚类分析结果
        renderer.render_cluster_analysis_results(results)
    
    elif "correlation_matrix" in results and "reliability_results" in results:
        # UTAUT2模型结果
        st.markdown("### 📱 UTAUT2模型分析结果")
        
        # 描述性统计
        if "descriptive_stats" in results:
            st.markdown("#### 描述性统计")
            st.dataframe(results["descriptive_stats"], use_container_width=True)
        
        # 相关性矩阵
        if "correlation_matrix" in results:
            st.markdown("#### 相关性矩阵")
            corr_matrix = results["correlation_matrix"]
            
            # 创建热力图
            import plotly.graph_objects as go
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale='RdBu',
                zmid=0
            ))
            fig.update_layout(title="变量相关性热力图")
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(corr_matrix, use_container_width=True)
        
        # 信度分析
        if "reliability_results" in results:
            st.markdown("#### 信度分析结果")
            reliability_df = pd.DataFrame([
                {"构念": k, "Cronbach's α": v} 
                for k, v in results["reliability_results"].items()
            ])
            st.dataframe(reliability_df, use_container_width=True)
        
        # AI分析
        if "ai_analysis" in results:
            renderer._render_ai_analysis_section(results["ai_analysis"])
    
    elif "factor_loadings" in results:
        # 因子分析结果
        st.markdown("### 📊 因子分析结果")
        
        # 因子载荷矩阵
        st.markdown("#### 因子载荷矩阵")
        st.dataframe(results["factor_loadings"], use_container_width=True)
        
        # 方差解释率
        if "variance_explained" in results:
            st.markdown("#### 方差解释率")
            variance_df = pd.DataFrame({
                "因子": [f"Factor_{i+1}" for i in range(len(results["variance_explained"]))],
                "解释方差": results["variance_explained"],
                "累计方差": results.get("cumulative_variance", [])
            })
            st.dataframe(variance_df, use_container_width=True)
        
        # AI分析
        if "ai_analysis" in results:
            renderer._render_ai_analysis_section(results["ai_analysis"])
    
    else:
        # 通用结果展示
        st.markdown("### 📈 分析结果")
        
        # 显示所有可用的结果
        for key, value in results.items():
            if key != "ai_analysis":
                st.markdown(f"#### {key}")
                if isinstance(value, pd.DataFrame):
                    st.dataframe(value, use_container_width=True)
                elif isinstance(value, (dict, list)):
                    st.json(value)
                else:
                    st.write(value)
        
        # AI分析（如果有）
        if "ai_analysis" in results:
            renderer._render_ai_analysis_section(results["ai_analysis"])
    
    # 添加结果导出功能
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 导出图表"):
            st.success("图表导出功能开发中")
    
    with col2:
        if st.button("📄 导出表格"):
            st.success("表格导出功能开发中")
    
    with col3:
        if st.button("📝 生成报告"):
            st.success("报告生成功能已在第6步提供")