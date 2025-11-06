"""
增强版AI数据分析系统 - 主界面
整合所有新功能：SPSS分析、学术报告、文献检索、模板上传等
"""

import sys
import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import json
from pathlib import Path
import logging
from typing import Optional, Dict, Any

# 设置页面配置
st.set_page_config(
    page_title="AI智能数据分析大模型系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入自定义模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 导入新增强模块
try:
    from src.data_processing.spss_analyzer import SPSSAnalyzer, AdvancedAnalysis
    from src.ai_agent.academic_engine import AcademicAnalysisEngine
    from src.ai_agent.literature_search import LiteratureSearchEngine, ReferenceIntegrator
    from src.report_generation.report_templates import ReportTemplateManager, SAMPLE_REPORTS
    from src.report_generation.template_uploader import (
        ReportTemplateUploader, TemplateApplier, 
        create_template_upload_interface, create_template_management_interface, 
        create_template_selection_interface
    )
    from src.visualization.advanced_visualizer import AdvancedVisualizer, ChartTemplateLibrary
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    ENHANCED_FEATURES_AVAILABLE = False
    st.error(f"⚠️ 增强功能模块导入失败: {e}")

# 导入原有模块
try:
    from src.model_selection.model_selector import ModelSelector
    from src.data_processing.data_loader import DataLoader
    from src.data_processing.data_processor import DataProcessor
    from src.visualization.visualizer import create_visualization_manager
    from src.report_generation.report_generator import create_advanced_report_generator
    from src.ai_agent.ai_assistant import create_ai_assistant
    from src.ai_agent.ai_report_enhancer import create_ai_enhancer
    CORE_FEATURES_AVAILABLE = True
except ImportError as e:
    CORE_FEATURES_AVAILABLE = False
    st.error(f"⚠️ 核心功能模块导入失败: {e}")

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置中文字体
try:
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass

class EnhancedDataAnalysisApp:
    """增强版数据分析应用"""
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_sidebar()
        
    def initialize_session_state(self):
        """初始化会话状态"""
        if 'data' not in st.session_state:
            st.session_state.data = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "数据上传"
        if 'research_topic' not in st.session_state:
            st.session_state.research_topic = ""
        if 'selected_template' not in st.session_state:
            st.session_state.selected_template = None
        if 'generated_reports' not in st.session_state:
            st.session_state.generated_reports = []
    
    def setup_sidebar(self):
        """设置侧边栏"""
        with st.sidebar:
            st.title("🎯 功能导航")
            
            # 主要功能页面
            pages = [
                "📤 数据上传",
                "📊 SPSS风格分析", 
                "📈 可视化分析",
                "🤖 AI智能分析",
                "📑 学术报告生成",
                "📚 文献检索",
                "📄 模板管理",
                "📋 报告历史",
                "⚙️ 系统设置"
            ]
            
            selected_page = st.selectbox("选择功能", pages, key="page_selector")
            st.session_state.current_page = selected_page.split(" ", 1)[1]  # 去掉emoji
            
            # 显示数据状态
            if st.session_state.data is not None:
                st.success(f"✅ 已加载数据\n{st.session_state.data.shape[0]} 行 × {st.session_state.data.shape[1]} 列")
            else:
                st.info("💡 请先上传数据文件")
            
            # 快速操作
            st.markdown("---")
            st.subheader("🚀 快速操作")
            
            if st.button("🧹 清除所有数据", help="清除当前会话的所有数据和结果"):
                self.clear_session_data()
                st.rerun()
            
            if st.button("💾 保存分析结果", help="保存当前分析结果"):
                self.save_analysis_results()
            
            # 显示系统信息
            st.markdown("---")
            st.subheader("ℹ️ 系统信息")
            st.info(f"""
            **版本**: v2.0 Enhanced
            **核心功能**: {'✅' if CORE_FEATURES_AVAILABLE else '❌'}
            **增强功能**: {'✅' if ENHANCED_FEATURES_AVAILABLE else '❌'}
            **支持格式**: CSV, Excel, JSON
            """)
    
    def run(self):
        """运行应用"""
        # 显示标题
        st.title("📊 AI智能数据分析大模型系统 Enhanced")
        st.markdown("---")
        
        # 根据选择的页面显示内容
        page_name = st.session_state.current_page
        
        if page_name == "数据上传":
            self.show_data_upload_page()
        elif page_name == "SPSS风格分析":
            self.show_spss_analysis_page()
        elif page_name == "可视化分析":
            self.show_visualization_page()
        elif page_name == "AI智能分析":
            self.show_ai_analysis_page()
        elif page_name == "学术报告生成":
            self.show_academic_report_page()
        elif page_name == "文献检索":
            self.show_literature_search_page()
        elif page_name == "模板管理":
            self.show_template_management_page()
        elif page_name == "报告历史":
            self.show_report_history_page()
        elif page_name == "系统设置":
            self.show_system_settings_page()
    
    def show_data_upload_page(self):
        """数据上传页面"""
        st.header("📤 数据上传与预览")
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "选择数据文件",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="支持CSV、Excel和JSON格式的数据文件"
        )
        
        if uploaded_file is not None:
            try:
                # 加载数据
                with st.spinner("正在加载数据..."):
                    # 先保存上传的文件到临时目录
                    temp_file_path = f"temp/{uploaded_file.name}"
                    os.makedirs("temp", exist_ok=True)
                    
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 使用DataLoader加载数据
                    data = DataLoader.load_data(temp_file_path)
                    
                    # 清理临时文件
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    
                    if data is not None:
                        st.session_state.data = data
                        st.success(f"✅ 数据加载成功！共 {data.shape[0]} 行，{data.shape[1]} 列")
                        
                        # 数据预览
                        st.subheader("📋 数据预览")
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.dataframe(data.head(10), use_container_width=True)
                        
                        with col2:
                            st.metric("总行数", data.shape[0])
                            st.metric("总列数", data.shape[1])
                            st.metric("缺失值", data.isnull().sum().sum())
                        
                        # 基本统计信息
                        st.subheader("📊 基本统计信息")
                        numeric_cols = data.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            st.dataframe(data[numeric_cols].describe(), use_container_width=True)
                        else:
                            st.info("没有发现数值型数据")
                        
                        # 数据类型信息
                        st.subheader("🏷️ 数据类型")
                        dtype_info = pd.DataFrame({
                            '列名': data.columns,
                            '数据类型': [str(dtype) for dtype in data.dtypes],
                            '非空值数量': [data[col].notna().sum() for col in data.columns],
                            '缺失值数量': [data[col].isna().sum() for col in data.columns]
                        })
                        st.dataframe(dtype_info, use_container_width=True)
                        
            except Exception as e:
                st.error(f"❌ 数据加载失败: {str(e)}")
        
        # 示例数据
        st.markdown("---")
        st.subheader("🎯 使用示例数据")
        
        if st.button("加载销售数据示例"):
            sample_data = self.create_sample_sales_data()
            st.session_state.data = sample_data
            st.success("✅ 示例数据加载成功！")
            st.rerun()
    
    def show_spss_analysis_page(self):
        """SPSS风格分析页面"""
        st.header("📊 SPSS风格数据分析")
        
        if not ENHANCED_FEATURES_AVAILABLE:
            st.error("❌ 增强功能不可用，请检查模块安装")
            return
        
        if st.session_state.data is None:
            st.warning("⚠️ 请先上传数据文件")
            return
        
        data = st.session_state.data
        analyzer = SPSSAnalyzer(data)
        
        # 分析选项
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_type = st.selectbox(
                "选择分析类型",
                [
                    "描述性统计",
                    "频数分析", 
                    "相关性分析",
                    "独立样本T检验",
                    "单因子方差分析",
                    "卡方检验",
                    "线性回归",
                    "主成分分析",
                    "聚类分析",
                    "信度分析"
                ]
            )
        
        with col2:
            if analysis_type in ["频数分析", "独立样本T检验", "单因子方差分析", "卡方检验"]:
                categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
                if categorical_cols:
                    selected_cat_var = st.selectbox("选择分类变量", categorical_cols)
                else:
                    st.warning("没有发现分类变量")
                    return
        
        # 变量选择
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
        if analysis_type == "描述性统计":
            if st.button("执行描述性统计分析"):
                with st.spinner("正在进行描述性统计分析..."):
                    results = analyzer.descriptive_statistics()
                    st.session_state.analysis_results['descriptive_stats'] = results
                    
                    # 显示结果
                    st.subheader("📈 描述性统计结果")
                    
                    # 创建汇总表
                    summary_data = []
                    for var, stats in results.items():
                        summary_data.append([
                            var,
                            f"{stats['样本量']:.0f}",
                            f"{stats['均值']:.3f}",
                            f"{stats['标准差']:.3f}",
                            f"{stats['最小值']:.3f}",
                            f"{stats['最大值']:.3f}",
                            f"{stats['偏度']:.3f}",
                            f"{stats['峰度']:.3f}",
                            stats['正态性']
                        ])
                    
                    summary_df = pd.DataFrame(
                        summary_data,
                        columns=['变量', '样本量', '均值', '标准差', '最小值', '最大值', '偏度', '峰度', '正态性']
                    )
                    
                    st.dataframe(summary_df, use_container_width=True)
                    
                    # 可视化
                    if ENHANCED_FEATURES_AVAILABLE:
                        visualizer = AdvancedVisualizer('academic')
                        fig = visualizer.create_descriptive_plots(data, numeric_cols)
                        if fig:
                            st.pyplot(fig)
        
        elif analysis_type == "相关性分析":
            correlation_method = st.selectbox("相关性方法", ["pearson", "spearman"])
            
            if st.button("执行相关性分析"):
                with st.spinner("正在进行相关性分析..."):
                    results = analyzer.correlation_analysis(correlation_method)
                    if results:
                        st.session_state.analysis_results['correlation_analysis'] = results
                        
                        # 显示相关性矩阵
                        st.subheader(f"📊 {correlation_method.title()}相关性矩阵")
                        st.dataframe(results['correlation_matrix'], use_container_width=True)
                        
                        # 显示p值
                        st.subheader("🔍 显著性检验 (p值)")
                        st.dataframe(results['p_values'], use_container_width=True)
                        
                        # 相关性解释
                        st.subheader("💡 相关性强度解释")
                        for pair, strength in results['interpretation'].items():
                            st.write(f"• **{pair}**: {strength}")
                        
                        # 可视化
                        if ENHANCED_FEATURES_AVAILABLE:
                            visualizer = AdvancedVisualizer('academic')
                            fig = visualizer.create_correlation_heatmap(data, numeric_cols, correlation_method)
                            if fig:
                                st.pyplot(fig)
        
        elif analysis_type == "独立样本T检验":
            if len(numeric_cols) > 0 and 'selected_cat_var' in locals():
                dependent_var = st.selectbox("选择因变量", numeric_cols)
                
                if st.button("执行T检验"):
                    with st.spinner("正在进行T检验..."):
                        results = analyzer.t_test_independent(dependent_var, selected_cat_var)
                        if results:
                            st.session_state.analysis_results['t_test'] = results
                            
                            # 显示结果
                            st.subheader("📊 独立样本T检验结果")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("组1均值", f"{results['group1_mean']:.3f}")
                                st.metric("组1标准差", f"{results['group1_std']:.3f}")
                                st.metric("组1样本量", results['group1_n'])
                            
                            with col2:
                                st.metric("组2均值", f"{results['group2_mean']:.3f}")
                                st.metric("组2标准差", f"{results['group2_std']:.3f}")
                                st.metric("组2样本量", results['group2_n'])
                            
                            # 检验结果
                            st.subheader("🔬 检验统计量")
                            st.write(f"**方差齐性检验**: Levene统计量 = {results['levene_statistic']:.3f}, p = {results['levene_p_value']:.3f}")
                            st.write(f"**方差齐性**: {results['variance_equal']}")
                            st.write(f"**T统计量**: {results['t_statistic']:.3f}")
                            st.write(f"**p值**: {results['p_value']:.3f}")
                            st.write(f"**Cohen's d**: {results['cohens_d']:.3f} ({results['effect_size']})")
                            st.write(f"**统计显著性**: {results['significant']}")
        
        # 其他分析类型的实现...
        # （为了节省空间，这里只展示几个主要的分析类型）
    
    def show_visualization_page(self):
        """可视化分析页面"""
        st.header("📈 高级可视化分析")
        
        if st.session_state.data is None:
            st.warning("⚠️ 请先上传数据文件")
            return
        
        data = st.session_state.data
        
        if ENHANCED_FEATURES_AVAILABLE:
            visualizer = AdvancedVisualizer()
            
            # 可视化选项
            viz_type = st.selectbox(
                "选择图表类型",
                [
                    "综合描述性统计图",
                    "相关性热力图",
                    "回归分析图",
                    "分组比较图",
                    "时间序列图",
                    "统计报告图表",
                    "交互式仪表板"
                ]
            )
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if viz_type == "综合描述性统计图" and len(numeric_cols) >= 2:
                selected_vars = st.multiselect("选择变量", numeric_cols, default=numeric_cols[:4])
                
                if st.button("生成描述性统计图"):
                    fig = visualizer.create_descriptive_plots(data, selected_vars)
                    if fig:
                        st.pyplot(fig)
                        
                        # 保存选项
                        if st.button("保存高质量图片"):
                            save_path = visualizer.save_high_quality_plot(fig, "descriptive_stats", "png", 300)
                            st.success(f"图片已保存到: {save_path}")
            
            elif viz_type == "相关性热力图" and len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    selected_vars = st.multiselect("选择变量", numeric_cols, default=numeric_cols)
                    method = st.selectbox("相关性方法", ["pearson", "spearman", "kendall"])
                
                with col2:
                    annotate = st.checkbox("显示数值", True)
                
                if st.button("生成相关性热力图"):
                    fig = visualizer.create_correlation_heatmap(data, selected_vars, method, annotate)
                    if fig:
                        st.pyplot(fig)
            
            elif viz_type == "回归分析图" and len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_var = st.selectbox("X变量", numeric_cols)
                with col2:
                    y_var = st.selectbox("Y变量", [col for col in numeric_cols if col != x_var])
                
                include_stats = st.checkbox("包含统计信息", True)
                
                if st.button("生成回归图"):
                    fig = visualizer.create_regression_plot(data, x_var, y_var, include_stats)
                    if fig:
                        st.pyplot(fig)
            
            elif viz_type == "分组比较图" and len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                col1, col2 = st.columns(2)
                with col1:
                    continuous_var = st.selectbox("连续变量", numeric_cols)
                with col2:
                    categorical_var = st.selectbox("分类变量", categorical_cols)
                
                if st.button("生成分组比较图"):
                    fig = visualizer.create_box_plot_comparison(data, continuous_var, categorical_var)
                    if fig:
                        st.pyplot(fig)
            
            elif viz_type == "交互式仪表板":
                if st.button("生成交互式仪表板"):
                    analysis_results = st.session_state.analysis_results
                    fig = visualizer.create_interactive_dashboard(data, analysis_results)
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.error("❌ 高级可视化功能不可用")
    
    def show_ai_analysis_page(self):
        """AI智能分析页面"""
        st.header("🤖 AI智能分析")
        
        if st.session_state.data is None:
            st.warning("⚠️ 请先上传数据文件")
            return
        
        # 研究主题设置
        research_topic = st.text_input(
            "研究主题",
            value=st.session_state.research_topic,
            placeholder="例如：消费者行为分析、销售趋势预测等"
        )
        st.session_state.research_topic = research_topic
        
        # AI分析选项
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_depth = st.selectbox(
                "分析深度",
                ["基础分析", "深度分析", "专业分析"]
            )
        
        with col2:
            ai_provider = st.selectbox(
                "AI服务提供商",
                ["通义千问", "OpenAI", "本地模型"]
            )
        
        # AI分析类型
        ai_analysis_types = st.multiselect(
            "选择AI分析类型",
            [
                "数据质量评估",
                "变量关系发现",
                "异常值检测",
                "模式识别",
                "预测建议",
                "商业洞察",
                "学术见解"
            ],
            default=["数据质量评估", "变量关系发现"]
        )
        
        if st.button("🚀 开始AI分析", type="primary"):
            if not research_topic:
                st.warning("请输入研究主题")
                return
            
            with st.spinner("AI正在分析数据..."):
                # 这里集成AI分析逻辑
                ai_results = self.perform_ai_analysis(
                    st.session_state.data, 
                    research_topic, 
                    analysis_depth, 
                    ai_analysis_types
                )
                
                if ai_results:
                    st.session_state.analysis_results['ai_analysis'] = ai_results
                    
                    # 显示AI分析结果
                    st.subheader("🧠 AI分析结果")
                    
                    for analysis_type, result in ai_results.items():
                        with st.expander(f"📊 {analysis_type}"):
                            st.write(result)
    
    def show_academic_report_page(self):
        """学术报告生成页面"""
        st.header("📑 学术报告生成")
        
        if not ENHANCED_FEATURES_AVAILABLE:
            st.error("❌ 学术报告功能不可用")
            return
        
        if not st.session_state.analysis_results:
            st.warning("⚠️ 请先进行数据分析")
            return
        
        # 报告类型选择
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "报告类型",
                ["学术论文", "商业报告", "期刊论文", "技术报告"]
            )
        
        with col2:
            citation_style = st.selectbox(
                "引用格式",
                ["APA", "MLA", "Chicago", "GB/T 7714"]
            )
        
        # 模板选择
        st.subheader("📄 选择报告模板")
        template_id = create_template_selection_interface()
        
        # 文献集成
        include_literature = st.checkbox("集成相关文献", True)
        
        if include_literature:
            literature_databases = st.multiselect(
                "文献数据库",
                ["知网(CNKI)", "万方", "PubMed", "Google Scholar"],
                default=["知网(CNKI)"]
            )
        
        # 生成报告
        if st.button("📝 生成学术报告", type="primary"):
            with st.spinner("正在生成学术报告..."):
                # 创建学术分析引擎
                academic_engine = AcademicAnalysisEngine()
                
                # 生成报告
                report_result = academic_engine.generate_academic_report(
                    st.session_state.analysis_results,
                    report_type.lower().replace(" ", "_"),
                    template_id
                )
                
                if include_literature and st.session_state.research_topic:
                    # 集成文献
                    ref_integrator = ReferenceIntegrator()
                    enhanced_report = ref_integrator.enhance_report_with_references(
                        str(report_result),
                        st.session_state.research_topic,
                        st.session_state.analysis_results,
                        citation_style
                    )
                    
                    report_result.update(enhanced_report)
                
                # 保存报告
                report_id = self.save_generated_report(report_result, report_type)
                
                # 显示报告
                st.subheader("📋 生成的学术报告")
                
                if "sections" in report_result:
                    for section_name, content in report_result["sections"].items():
                        with st.expander(f"📄 {section_name.replace('_', ' ').title()}"):
                            st.write(content)
                
                # 下载选项
                if st.button("💾 下载报告"):
                    self.download_report(report_result, f"{report_type}_{report_id}")
    
    def show_literature_search_page(self):
        """文献检索页面"""
        st.header("📚 学术文献检索")
        
        if not ENHANCED_FEATURES_AVAILABLE:
            st.error("❌ 文献检索功能不可用")
            return
        
        # 检索设置
        col1, col2 = st.columns(2)
        
        with col1:
            keywords = st.text_input(
                "检索关键词",
                placeholder="输入关键词，用空格或逗号分隔"
            )
            
            databases = st.multiselect(
                "选择数据库",
                ["知网(CNKI)", "万方", "PubMed", "Google Scholar"],
                default=["知网(CNKI)", "万方"]
            )
        
        with col2:
            max_results = st.slider("最大结果数", 5, 50, 20)
            
            year_range = st.slider(
                "年份范围",
                2000, 2024, (2020, 2024)
            )
        
        # 执行检索
        if st.button("🔍 开始检索", type="primary") and keywords:
            keyword_list = [kw.strip() for kw in keywords.replace(',', ' ').split()]
            
            with st.spinner("正在检索文献..."):
                search_engine = LiteratureSearchEngine()
                
                db_mapping = {
                    "知网(CNKI)": "cnki",
                    "万方": "wanfang", 
                    "PubMed": "pubmed",
                    "Google Scholar": "google_scholar"
                }
                
                selected_dbs = [db_mapping[db] for db in databases if db in db_mapping]
                
                results = search_engine.search_literature(
                    keyword_list,
                    selected_dbs,
                    max_results,
                    year_range
                )
                
                # 显示检索结果
                st.subheader(f"📊 检索结果 (共找到 {sum(len(papers) for papers in results.values())} 篇文献)")
                
                for db_name, papers in results.items():
                    if papers:
                        with st.expander(f"📚 {db_name.upper()} ({len(papers)} 篇)"):
                            for i, paper in enumerate(papers):
                                st.markdown(f"**{i+1}. {paper['title']}**")
                                st.write(f"作者: {', '.join(paper['authors'])}")
                                st.write(f"期刊: {paper['journal']} ({paper['year']})")
                                st.write(f"相关性: {paper['relevance_score']:.2f}")
                                
                                if st.button(f"查看详情", key=f"detail_{db_name}_{i}"):
                                    with st.expander("详细信息", expanded=True):
                                        st.write(f"**摘要**: {paper.get('abstract', '无摘要')}")
                                        st.write(f"**关键词**: {', '.join(paper.get('keywords', []))}")
                                        st.write(f"**DOI**: {paper.get('doi', '无')}")
                                        
                                        if 'full_citation' in paper:
                                            st.write("**引用格式**:")
                                            for style, citation in paper['full_citation'].items():
                                                st.code(citation, language="text")
                                
                                st.markdown("---")
        
        # 引用管理
        st.subheader("📎 引用管理")
        
        if st.button("生成参考文献"):
            # 这里可以集成用户选择的文献，生成参考文献列表
            st.info("请先检索并选择文献")
    
    def show_template_management_page(self):
        """模板管理页面"""
        st.header("📄 报告模板管理")
        
        if not ENHANCED_FEATURES_AVAILABLE:
            st.error("❌ 模板管理功能不可用")
            return
        
        tab1, tab2, tab3 = st.tabs(["📤 上传模板", "📚 模板库", "🎨 模板预览"])
        
        with tab1:
            create_template_upload_interface()
        
        with tab2:
            create_template_management_interface()
        
        with tab3:
            st.subheader("📋 内置模板预览")
            
            template_manager = ReportTemplateManager()
            template_types = list(template_manager.templates.keys())
            
            selected_template_type = st.selectbox("选择模板类型", template_types)
            
            if selected_template_type:
                template = template_manager.get_template(selected_template_type)
                
                st.write(f"**模板类型**: {template['type']}")
                st.write(f"**章节结构**: {', '.join(template['structure'])}")
                
                # 显示章节详情
                for section_name in template['structure'][:5]:  # 只显示前5个章节
                    if section_name in template['sections']:
                        section = template['sections'][section_name]
                        with st.expander(f"📝 {section_name.replace('_', ' ').title()}"):
                            st.write(f"**格式**: {section.get('format', '未定义')}")
                            st.write(f"**指导**: {section.get('guidelines', '无')}")
    
    def show_report_history_page(self):
        """报告历史页面"""
        st.header("📋 报告历史")
        
        if not st.session_state.generated_reports:
            st.info("暂无生成的报告")
            return
        
        # 显示报告列表
        for i, report in enumerate(st.session_state.generated_reports):
            with st.expander(f"📄 报告 {i+1}: {report.get('title', f'报告_{i+1}')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**类型**: {report.get('type', '未知')}")
                    st.write(f"**生成时间**: {report.get('timestamp', '未知')}")
                
                with col2:
                    st.write(f"**字数**: {report.get('word_count', 0)}")
                    st.write(f"**引用数**: {report.get('citation_count', 0)}")
                
                with col3:
                    if st.button(f"查看", key=f"view_{i}"):
                        st.session_state.current_report = report
                    
                    if st.button(f"下载", key=f"download_{i}"):
                        self.download_report(report, f"report_{i}")
    
    def show_system_settings_page(self):
        """系统设置页面"""
        st.header("⚙️ 系统设置")
        
        # AI设置
        st.subheader("🤖 AI设置")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_ai_provider = st.selectbox(
                "默认AI服务商",
                ["通义千问", "OpenAI", "本地模型"],
                help="选择默认使用的AI服务商"
            )
            
            ai_enhancement_enabled = st.checkbox(
                "启用AI增强功能",
                True,
                help="是否启用AI报告增强功能"
            )
        
        with col2:
            max_tokens = st.slider("最大生成长度", 1000, 8000, 4000)
            temperature = st.slider("创造性程度", 0.0, 1.0, 0.7)
        
        # 可视化设置
        st.subheader("📊 可视化设置")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_chart_style = st.selectbox(
                "默认图表风格",
                ["学术风格", "商务风格", "现代风格"]
            )
            
            chart_dpi = st.slider("图表分辨率(DPI)", 150, 300, 300)
        
        with col2:
            color_palette = st.selectbox(
                "颜色主题",
                ["默认", "科学", "商务", "现代"]
            )
        
        # 报告设置
        st.subheader("📝 报告设置")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_citation_style = st.selectbox(
                "默认引用格式",
                ["APA", "MLA", "Chicago", "GB/T 7714"]
            )
            
            auto_literature_search = st.checkbox(
                "自动文献检索",
                False,
                help="生成报告时自动检索相关文献"
            )
        
        with col2:
            max_literature_count = st.slider("最大文献数量", 5, 30, 15)
        
        # 保存设置
        if st.button("💾 保存设置", type="primary"):
            settings = {
                "ai": {
                    "default_provider": default_ai_provider,
                    "enhancement_enabled": ai_enhancement_enabled,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                "visualization": {
                    "default_style": default_chart_style,
                    "dpi": chart_dpi,
                    "color_palette": color_palette
                },
                "report": {
                    "default_citation_style": default_citation_style,
                    "auto_literature_search": auto_literature_search,
                    "max_literature_count": max_literature_count
                }
            }
            
            self.save_user_settings(settings)
            st.success("✅ 设置已保存")
    
    # 辅助方法
    def create_sample_sales_data(self):
        """创建示例销售数据"""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            '产品ID': [f'P{i:04d}' for i in range(1, n_samples + 1)],
            '产品类别': np.random.choice(['电子产品', '服装', '家居', '食品', '图书'], n_samples),
            '销售额': np.random.normal(5000, 2000, n_samples).clip(min=100),
            '销售量': np.random.poisson(50, n_samples),
            '客户年龄': np.random.normal(35, 12, n_samples).clip(min=18, max=80),
            '客户性别': np.random.choice(['男', '女'], n_samples),
            '地区': np.random.choice(['北京', '上海', '广州', '深圳', '杭州'], n_samples),
            '促销活动': np.random.choice(['是', '否'], n_samples, p=[0.3, 0.7]),
            '满意度评分': np.random.uniform(1, 5, n_samples)
        }
        
        return pd.DataFrame(data)
    
    def perform_ai_analysis(self, data, research_topic, depth, analysis_types):
        """执行AI分析"""
        # 这里是AI分析的简化实现
        results = {}
        
        for analysis_type in analysis_types:
            if analysis_type == "数据质量评估":
                results[analysis_type] = f"数据集包含{data.shape[0]}行{data.shape[1]}列，缺失值率为{(data.isnull().sum().sum() / (data.shape[0] * data.shape[1]) * 100):.1f}%。数据质量整体良好。"
            
            elif analysis_type == "变量关系发现":
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    corr_matrix = data[numeric_cols].corr()
                    max_corr = corr_matrix.abs().unstack().sort_values(ascending=False)
                    max_corr = max_corr[max_corr < 1.0].iloc[0]
                    results[analysis_type] = f"发现最强相关关系，相关系数为{max_corr:.3f}。建议进一步探索这些变量间的因果关系。"
                else:
                    results[analysis_type] = "数据中数值变量不足，无法进行相关性分析。"
            
            # 添加更多AI分析逻辑...
        
        return results
    
    def save_generated_report(self, report_result, report_type):
        """保存生成的报告"""
        report_id = f"report_{len(st.session_state.generated_reports) + 1}"
        
        report_record = {
            "id": report_id,
            "title": f"{report_type}_报告",
            "type": report_type,
            "content": report_result,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": sum(len(str(content).split()) for content in report_result.get("sections", {}).values()),
            "citation_count": report_result.get("citation_count", 0)
        }
        
        st.session_state.generated_reports.append(report_record)
        return report_id
    
    def download_report(self, report, filename):
        """下载报告"""
        # 简化的下载实现
        st.info(f"报告 {filename} 下载功能待实现")
    
    def clear_session_data(self):
        """清除会话数据"""
        st.session_state.data = None
        st.session_state.analysis_results = {}
        st.session_state.generated_reports = []
        st.session_state.research_topic = ""
    
    def save_analysis_results(self):
        """保存分析结果"""
        if st.session_state.analysis_results:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_results_{timestamp}.json"
            
            try:
                os.makedirs("temp/saved_results", exist_ok=True)
                with open(f"temp/saved_results/{filename}", 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.analysis_results, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 分析结果已保存: {filename}")
            except Exception as e:
                st.error(f"❌ 保存失败: {e}")
        else:
            st.warning("没有分析结果可保存")
    
    def save_user_settings(self, settings):
        """保存用户设置"""
        try:
            os.makedirs("temp", exist_ok=True)
            with open("temp/user_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"设置保存失败: {e}")

# 主程序入口
def main():
    """主程序"""
    try:
        app = EnhancedDataAnalysisApp()
        app.run()
    except Exception as e:
        st.error(f"应用运行错误: {e}")
        logger.error(f"Application error: {e}", exc_info=True)

if __name__ == "__main__":
    main()