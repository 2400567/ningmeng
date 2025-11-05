"""
AI数据分析系统 - 用户界面模块

使用Streamlit创建交互式Web界面，提供：
1. 文件上传功能
2. 数据预览
3. 模型选择
4. 分析结果展示
5. 报告导出
"""

import sys
import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import uuid
import base64
import matplotlib.pyplot as plt
from pathlib import Path
import logging
from typing import Optional, Dict, Any

# 导入自定义模块
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.model_selection.model_selector import ModelSelector, ModelRecommendation
from src.data_processing.data_loader import DataLoader, DataValidator
from src.data_processing.data_processor import DataProcessor
from src.visualization.visualizer import create_visualization_manager
from src.report_generation.report_generator import create_advanced_report_generator
from src.ai_agent.ai_assistant import create_ai_assistant

# 导入AI增强模块
try:
    from src.ai_agent.ai_report_enhancer import create_ai_enhancer, DEFAULT_CONFIGS, AIModelConfig, AIReportEnhancer
    AI_ENHANCEMENT_AVAILABLE = True
except ImportError:
    AI_ENHANCEMENT_AVAILABLE = False
    st.warning("⚠️ AI报告增强功能不可用，请检查相关依赖")

logger = logging.getLogger(__name__)


class AppState:
    """应用状态管理类"""
    
    @staticmethod
    def initialize_session_state():
        """初始化会话状态"""
        # 在会话初始化时清理过期的临时图像文件
        try:
            clean_temp_figures()
        except Exception:
            pass
        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None
        if 'data' not in st.session_state:
            st.session_state.data = None
        if 'processed_data' not in st.session_state:
            st.session_state.processed_data = None
        if 'data_info' not in st.session_state:
            st.session_state.data_info = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'descriptive_stats' not in st.session_state:
            st.session_state.descriptive_stats = None
        if 'correlation_matrix' not in st.session_state:
            st.session_state.correlation_matrix = None
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = None
        if 'progress' not in st.session_state:
            st.session_state.progress = 0
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 'upload'  # upload, analyze, visualize, report
        if 'current_section' not in st.session_state:
            st.session_state.current_section = 'upload'  # 添加current_section的初始化
        if 'file_name' not in st.session_state:
            st.session_state.file_name = None
        if 'file_format' not in st.session_state:
            st.session_state.file_format = None
        if 'report_path' not in st.session_state:
            st.session_state.report_path = None
        if 'preprocessing_info' not in st.session_state:
            st.session_state.preprocessing_info = {}
        # AI助手相关状态
        if 'ai_assistant' not in st.session_state:
            st.session_state.ai_assistant = create_ai_assistant()
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'show_ai_assistant' not in st.session_state:
            st.session_state.show_ai_assistant = False
        
        # AI报告增强相关状态
        if 'ai_enhancement_enabled' not in st.session_state:
            st.session_state.ai_enhancement_enabled = False
        if 'ai_provider' not in st.session_state:
            st.session_state.ai_provider = "openai"
        if 'ai_model' not in st.session_state:
            st.session_state.ai_model = "gpt-3.5-turbo"
        if 'ai_api_key' not in st.session_state:
            st.session_state.ai_api_key = ""
        if 'ai_api_base' not in st.session_state:
            st.session_state.ai_api_base = ""
        if 'ai_enhancement_type' not in st.session_state:
            st.session_state.ai_enhancement_type = "comprehensive"


def set_page_config():
    """设置Streamlit页面配置"""
    st.set_page_config(
        page_title="AI智能数据分析系统",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def run_app():
    """运行Streamlit应用（供main.py调用）"""
    # 初始化会话状态
    AppState.initialize_session_state()
    # 设置页面配置
    set_page_config()
    # 这里会执行Streamlit应用的主要逻辑
    # Streamlit会自动执行文件中的代码
    pass


def clean_temp_figures(max_age_seconds: int = 7 * 24 * 3600):
    """
    清理 `temp/figures` 下超过指定年龄的临时图像文件。默认保留 7 天。
    在应用初始化时调用以防目录无限膨胀。
    """
    try:
        temp_dir = Path("temp/figures")
        if not temp_dir.exists():
            return
        now = time.time()
        for p in temp_dir.iterdir():
            try:
                if p.is_file():
                    mtime = p.stat().st_mtime
                    if now - mtime > max_age_seconds:
                        p.unlink()
            except Exception:
                # 忽略单个文件删除错误
                pass
    except Exception:
        pass


def safe_display_figure(fig):
    """
    安全地在 Streamlit 中显示 matplotlib Figure。
    尝试使用 st.pyplot 显示；如果遇到 Streamlit 的媒体文件存储错误或其他异常，
    回退为将图像编码为 base64 并使用 st.image 显示（这样可以避免 MediaFileStorageError）。
    此函数会在必要时关闭 figure。
    """
    try:
        # 为了避免 Streamlit 内部媒体 id 丢失或并发回收问题，
        # 我们把 figure 保存为临时文件并直接通过文件路径显示（st.image）——更稳健。
        temp_dir = Path("temp/figures")
        temp_dir.mkdir(parents=True, exist_ok=True)
        fname = f"fig_{int(time.time())}_{uuid.uuid4().hex}.png"
        file_path = temp_dir / fname
        try:
            fig.savefig(file_path, dpi=150, bbox_inches='tight')
        except Exception as e_save:
            # 如果直接保存失败，回退到 DataVisualizer 的 base64 方法
            try:
                from src.visualization.visualizer import DataVisualizer
                viz = DataVisualizer()
                img_b64 = viz.figure_to_base64(fig)
                st.image(base64.b64decode(img_b64), use_column_width=True)
                return
            except Exception:
                st.write(f"无法渲染图表（保存与base64回退均失败）: {e_save}")
                try:
                    plt.close(fig)
                except Exception:
                    pass
                return

        # 显示图片并记录（不主动删除，便于调试；可周期性清理 temp/figures）
        st.image(str(file_path), use_column_width=True)
    finally:
        try:
            plt.close(fig)
        except Exception:
            pass


def display_header():
    """显示应用标题和描述以及AI助手按钮"""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #2c3e50;'>📊 AI智能数据分析大模型系统</h1>
            <p style='color: #7f8c8d; font-size: 18px;'>自动化数据处理、智能分析、可视化与专业报告生成</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        # AI助手切换按钮
        st.session_state.show_ai_assistant = st.toggle(
            "💬 AI助手", 
            value=st.session_state.show_ai_assistant,
            help="打开AI智能助手，获取数据分析建议"
        )
    
    # 显示进度指示器
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; {'background-color: #2ecc71; color: white;' if st.session_state.current_step in ['analyze', 'visualize', 'report'] else 'background-color: #ecf0f1;'} border-radius: 5px;'>
            <h4>1️⃣ 导入数据</h4>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; {'background-color: #2ecc71; color: white;' if st.session_state.current_step in ['visualize', 'report'] else 'background-color: #ecf0f1;'} border-radius: 5px;'>
            <h4>2️⃣ 分析数据</h4>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; {'background-color: #2ecc71; color: white;' if st.session_state.current_step == 'report' else 'background-color: #ecf0f1;'} border-radius: 5px;'>
            <h4>3️⃣ 生成图表</h4>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; background-color: #ecf0f1; border-radius: 5px;'>
            <h4>4️⃣ 生成报告</h4>
        </div>
        """, unsafe_allow_html=True)


def file_upload_section():
    """文件上传部分"""
    st.subheader("📥 数据导入")
    
    # 显示支持的文件格式
    supported_formats = DataLoader.get_supported_formats()
    st.info(f"支持的文件格式: {', '.join(supported_formats)}")
    
    # 文件上传组件
    uploaded_file = st.file_uploader(
        "选择数据文件",
        type=[fmt[1:] for fmt in supported_formats],  # 移除点号
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # 保存到会话状态
        st.session_state.uploaded_file = uploaded_file
        
        # 显示文件信息
        st.success(f"已上传文件: {uploaded_file.name}")
        st.write(f"文件大小: {uploaded_file.size / 1024:.2f} KB")
        
        # 创建一个临时目录保存上传的文件
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / uploaded_file.name
        
        # 保存上传的文件到临时目录
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 显示进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(progress):
            progress_bar.progress(progress)
            status_text.text(f"加载中... {progress}%")
        
        # 尝试加载数据
        load_success = False
        try:
            # 使用进度回调加载数据
            df = DataLoader.load_data_with_progress(
                temp_file_path,
                progress_callback=update_progress
            )

            # 验证数据
            data_info = DataValidator.validate_data(df)

            # 保存到会话状态
            st.session_state.data = df
            st.session_state.data_info = data_info
            load_success = True

            # 显示数据基本信息
            st.subheader("📊 数据预览")
            col1, col2 = st.columns([1, 2])

            with col1:
                st.write("### 数据信息")
                st.write(f"行数: {data_info['n_rows']}")
                st.write(f"列数: {data_info['n_columns']}")
                st.write(f"数值型列数: {len(df.select_dtypes(include=['number']).columns)}")
                st.write(f"缺失值总数: {sum(data_info['missing_values'].values())}")

            with col2:
                st.write("### 前5行数据")
                st.dataframe(df.head())

            # 显示数据类型和缺失值
            st.write("### 列信息")
            info_df = pd.DataFrame({
                '数据类型': df.dtypes.astype(str),
                '缺失值': df.isnull().sum(),
                '唯一值数量': df.nunique()
            })
            st.dataframe(info_df)

            # 检查是否有问题
            if data_info['issues']:
                st.warning("⚠️ 数据可能存在以下问题:")
                for issue in data_info['issues']:
                    st.warning(f"- {issue}")

            # 下一步按钮
            if st.button("🔍 开始分析", use_container_width=True):
                st.session_state.current_step = 'analyze'
                st.rerun()

        except Exception as e:
            # 在 UI 直接显示完整异常，便于用户快速定位问题
            st.error(f"❌ 文件加载失败: {str(e)}")
            try:
                st.exception(e)
            except Exception:
                # 在某些环境下 st.exception 可能无法呈现复杂对象，保证至少显示文本
                st.write(repr(e))
            logger.error(f"文件加载失败: {str(e)}", exc_info=True)
            # 提示用户可能的原因和排查建议
            st.info("排查建议: 1) 检查文件格式是否被支持（CSV/XLSX/JSON/TXT/Parquet）；2) 如果是 Excel，请确保已安装 openpyxl；3) 文件是否被加密或损坏。")
        finally:
            # 清理临时文件：如果加载成功则删除临时文件，否则保留以便调试，并在 UI 中给出路径
            try:
                if load_success:
                    if temp_file_path.exists():
                        temp_file_path.unlink()
                else:
                    if temp_file_path.exists():
                        st.info(f"已保留上传的临时文件以便调试: {temp_file_path}")
                        logger.info(f"保留临时上传文件用于调试: {temp_file_path}")
            except Exception as e_cleanup:
                logger.warning(f"清理临时文件时出错: {e_cleanup}")
    else:
        # 重置会话状态
        if st.session_state.data is not None:
            st.session_state.data = None
            st.session_state.data_info = None


def analyze_section():
    """数据分析部分 - 按照SPSSAU模板设计"""
    st.subheader("� 数据分析 - SPSSAU模板")
    
    # 检查是否有数据
    if st.session_state.data is None:
        st.error("请先上传数据!")
        if st.button("返回上传"):
            st.session_state.current_step = 'upload'
            st.rerun()
        return
    
    # 创建数据处理器实例
    processor = DataProcessor()
    
    # 使用处理后的数据或原始数据
    current_data = st.session_state.processed_data if 'processed_data' in st.session_state and st.session_state.processed_data is not None else st.session_state.data
    
    # SPSSAU风格的分析模块选择
    st.write("### 📋 选择分析模块")
    
    analysis_modules = {
        "数据处理": {
            "icon": "🔧",
            "description": "数据清洗、编码、特征工程等基础处理",
            "options": ["数据清洗", "数据编码", "生成变量", "数据标签设置"]
        },
        "通用方法": {
            "icon": "📈", 
            "description": "频数分析、描述统计、交叉分析等常用方法",
            "options": ["频数分析", "描述统计", "交叉分析(卡方)", "相关分析", "独立样本t检验", "配对样本t检验"]
        },
        "问卷研究": {
            "icon": "📝",
            "description": "信度分析、效度分析、多选题等问卷专用分析",
            "options": ["信度分析", "效度分析", "多选题分析", "问卷质量评估"]
        },
        "进阶方法": {
            "icon": "🧠",
            "description": "回归分析、聚类、因子分析等高级统计方法",
            "options": ["线性回归", "逻辑回归", "聚类分析", "因子分析", "主成分分析", "方差分析"]
        },
        "机器学习": {
            "icon": "🤖",
            "description": "决策树、随机森林、神经网络等ML算法",
            "options": ["决策树", "随机森林", "支持向量机", "神经网络", "朴素贝叶斯", "KNN分类"]
        },
        "时间序列": {
            "icon": "📊",
            "description": "时间序列分析和预测",
            "options": ["趋势分析", "季节性分解", "ARIMA模型", "时序预测"]
        }
    }
    
    # 创建模块选择界面
    selected_module = st.selectbox(
        "选择分析模块",
        list(analysis_modules.keys()),
        format_func=lambda x: f"{analysis_modules[x]['icon']} {x}"
    )
    
    # 显示模块描述
    st.info(f"📝 {analysis_modules[selected_module]['description']}")
    
    # 显示选定模块的分析选项
    st.write(f"### {analysis_modules[selected_module]['icon']} {selected_module}")
    
    # 使用多选框让用户选择多个分析方法
    selected_analyses = st.multiselect(
        "选择要执行的分析方法（可多选）",
        analysis_modules[selected_module]['options'],
        help="您可以选择多个分析方法，系统将按顺序依次执行"
    )
    
    # 显示选中的分析方法
    if selected_analyses:
        st.write("**已选择的分析方法：**")
        for i, analysis in enumerate(selected_analyses, 1):
            st.write(f"{i}. {analysis}")
    
    # 批量分析选项
    if selected_analyses:
        col1, col2 = st.columns(2)
        with col1:
            auto_proceed = st.checkbox("自动执行所有分析", value=True, help="勾选后将依次执行所有选中的分析")
        with col2:
            save_individual_results = st.checkbox("保存每个分析的结果", value=True, help="为每个分析单独保存结果")
    
    # 执行选定的分析
    if selected_analyses and st.button(f"🚀 批量执行分析 ({len(selected_analyses)}个)", use_container_width=True):
        # 初始化批量分析结果
        batch_results = {}
        success_count = 0
        total_count = len(selected_analyses)
        
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.container():
            for i, analysis_option in enumerate(selected_analyses):
                progress = (i + 1) / total_count
                progress_bar.progress(progress)
                status_text.text(f"正在执行 ({i+1}/{total_count}): {analysis_option}")
                
                try:
                    with st.spinner(f"正在执行 {analysis_option}..."):
                        # 执行分析
                        analysis_result = execute_single_analysis(
                            selected_module, analysis_option, processor, current_data
                        )
                        
                        if analysis_result:
                            batch_results[analysis_option] = analysis_result
                            success_count += 1
                            
                            # 如果选择保存单独结果，则显示简要信息
                            if save_individual_results:
                                with st.expander(f"✅ {analysis_option} - 完成"):
                                    display_analysis_summary(analysis_result)
                        else:
                            st.warning(f"⚠️ {analysis_option} 执行失败或无结果")
                            
                        # 短暂暂停，让用户看到进度
                        if auto_proceed and i < len(selected_analyses) - 1:
                            import time
                            time.sleep(0.5)
                            
                except Exception as e:
                    st.error(f"❌ {analysis_option} 执行失败: {str(e)}")
                    batch_results[analysis_option] = {"error": str(e)}
        
        # 完成批量分析
        progress_bar.progress(1.0)
        status_text.text(f"批量分析完成！成功执行 {success_count}/{total_count} 个分析")
        
        # 保存批量结果
        st.session_state.batch_analysis_results = batch_results
        st.session_state.analysis_completed = True
        st.session_state.analysis_type = f"批量分析-{selected_module}"
        st.session_state.current_analysis_data = current_data
        
        # 显示汇总结果
        st.success(f"🎉 批量分析完成！成功执行了 {success_count} 个分析方法")
        
        # 显示批量分析汇总
        with st.expander("📊 批量分析结果汇总", expanded=True):
            display_batch_results_summary(batch_results)
    
    # 显示分析结果
    if hasattr(st.session_state, 'batch_analysis_results') and st.session_state.batch_analysis_results:
        display_batch_analysis_results()
    elif hasattr(st.session_state, 'analysis_results') and st.session_state.analysis_results:
        display_analysis_results()
    
    # 下一步按钮
    if hasattr(st.session_state, 'analysis_completed') and st.session_state.analysis_completed:
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📈 下一步：数据可视化", use_container_width=True):
                st.session_state.current_step = 'visualize'
                st.rerun()
        with col2:
            if st.button("📄 直接生成报告", use_container_width=True):
                st.session_state.current_step = 'report'
                st.rerun()
    
    # 上一步按钮
    if st.button("⬅️ 返回数据上传", use_container_width=True):
        st.session_state.current_step = 'upload'
        st.rerun()


def execute_data_processing(analysis_option, processor, data):
    """执行数据处理分析"""
    if analysis_option == "数据清洗":
        execute_data_cleaning(processor, data)
    elif analysis_option == "数据编码":
        execute_data_encoding(processor, data)
    elif analysis_option == "生成变量":
        execute_variable_generation(processor, data)
    elif analysis_option == "数据标签设置":
        execute_data_labeling(processor, data)


def execute_data_cleaning(processor, data):
    """数据清洗功能"""
    st.write("#### 🔧 数据清洗")
    
    # 显示数据质量概览
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总行数", data.shape[0])
    with col2:
        missing_count = data.isnull().sum().sum()
        st.metric("缺失值数量", missing_count)
    with col3:
        duplicate_count = data.duplicated().sum()
        st.metric("重复行数", duplicate_count)
    
    # 缺失值处理选项
    st.write("##### 缺失值处理")
    missing_columns = data.columns[data.isnull().any()].tolist()
    if missing_columns:
        st.write("包含缺失值的列：", ", ".join(missing_columns))
        missing_strategy = st.selectbox(
            "选择处理策略",
            ["删除含缺失值的行", "均值填充(数值列)", "众数填充(所有列)", "前向填充", "后向填充"]
        )
        
        # 执行缺失值处理
        if missing_strategy == "删除含缺失值的行":
            cleaned_data = data.dropna()
        elif missing_strategy == "均值填充(数值列)":
            cleaned_data = data.copy()
            numeric_cols = data.select_dtypes(include=['number']).columns
            cleaned_data[numeric_cols] = cleaned_data[numeric_cols].fillna(cleaned_data[numeric_cols].mean())
        elif missing_strategy == "众数填充(所有列)":
            cleaned_data = data.fillna(data.mode().iloc[0])
        elif missing_strategy == "前向填充":
            cleaned_data = data.fillna(method='ffill')
        else:  # 后向填充
            cleaned_data = data.fillna(method='bfill')
            
        st.session_state.processed_data = cleaned_data
        st.success(f"缺失值处理完成！数据从 {data.shape[0]} 行变为 {cleaned_data.shape[0]} 行")
    else:
        st.success("数据中没有缺失值！")
    
    # 重复值处理
    if duplicate_count > 0:
        st.write("##### 重复值处理")
        if st.button("删除重复行"):
            cleaned_data = data.drop_duplicates()
            st.session_state.processed_data = cleaned_data
            st.success(f"已删除 {duplicate_count} 行重复数据")
    
    # 显示清洗后的数据预览
    current_data = st.session_state.processed_data if 'processed_data' in st.session_state else data
    st.write("##### 数据预览")
    st.dataframe(current_data.head())


def execute_general_methods(analysis_option, processor, data):
    """执行通用方法分析"""
    if analysis_option == "频数分析":
        execute_frequency_analysis(data)
    elif analysis_option == "描述统计":
        execute_descriptive_statistics(data)
    elif analysis_option == "交叉分析(卡方)":
        execute_crosstab_analysis(data)
    elif analysis_option == "相关分析":
        execute_correlation_analysis(data)
    elif analysis_option == "独立样本t检验":
        execute_independent_ttest(data)
    elif analysis_option == "配对样本t检验":
        execute_paired_ttest(data)


def execute_frequency_analysis(data):
    """频数分析"""
    st.write("#### 📊 频数分析")
    
    # 选择要分析的列
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    all_cols = categorical_cols + numeric_cols
    selected_col = st.selectbox("选择要分析的变量", all_cols)
    
    if selected_col:
        # 计算频数
        if selected_col in categorical_cols:
            freq_table = data[selected_col].value_counts().reset_index()
            freq_table.columns = ['类别', '频数']
            freq_table['百分比'] = (freq_table['频数'] / freq_table['频数'].sum() * 100).round(2)
        else:
            # 数值列进行分组
            bins = st.slider("选择分组数", 5, 20, 10)
            freq_table = pd.cut(data[selected_col], bins=bins).value_counts().reset_index()
            freq_table.columns = ['区间', '频数'] 
            freq_table['百分比'] = (freq_table['频数'] / freq_table['频数'].sum() * 100).round(2)
        
        # 显示结果
        st.write("##### 频数分布表")
        st.dataframe(freq_table)
        
        # 存储结果
        st.session_state.analysis_results = {
            'type': '频数分析',
            'variable': selected_col,
            'frequency_table': freq_table
        }
        
        st.success("频数分析完成！")


def execute_descriptive_statistics(data):
    """描述统计"""
    st.write("#### 📈 描述统计")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if not numeric_cols:
        st.error("没有数值型变量可以进行描述统计")
        return
    
    selected_cols = st.multiselect("选择要分析的数值变量", numeric_cols, default=numeric_cols[:5])
    
    if selected_cols:
        # 计算描述统计
        desc_stats = data[selected_cols].describe().round(3)
        
        # 添加更多统计量
        additional_stats = pd.DataFrame({
            col: {
                '偏度': data[col].skew(),
                '峰度': data[col].kurtosis(),
                '变异系数': data[col].std() / data[col].mean() if data[col].mean() != 0 else 0
            } for col in selected_cols
        }).round(3)
        
        # 合并统计结果
        full_stats = pd.concat([desc_stats, additional_stats])
        
        st.write("##### 描述统计结果")
        st.dataframe(full_stats)
        
        # 存储结果
        st.session_state.analysis_results = {
            'type': '描述统计',
            'variables': selected_cols,
            'descriptive_stats': full_stats
        }
        
        st.success("描述统计分析完成！")


def execute_questionnaire_analysis(analysis_option, processor, data):
    """执行问卷研究分析"""
    if analysis_option == "信度分析":
        execute_reliability_analysis(processor, data)
    elif analysis_option == "效度分析":
        execute_validity_analysis(processor, data)
    elif analysis_option == "多选题分析":
        execute_multiple_choice_analysis(data)
    elif analysis_option == "问卷质量评估":
        execute_questionnaire_quality(data)


def execute_reliability_analysis(processor, data):
    """信度分析（克朗巴赫α系数）"""
    st.write("#### 📝 信度分析")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 2:
        st.error("信度分析需要至少2个数值型变量")
        return
    
    selected_cols = st.multiselect(
        "选择构成量表的题目变量", 
        numeric_cols,
        help="选择属于同一个量表或维度的题目"
    )
    
    if len(selected_cols) >= 2:
        try:
            # 执行信度分析
            reliability_results = processor.reliability_analysis(data[selected_cols])
            
            st.write("##### 信度分析结果")
            
            # 显示Cronbach's Alpha
            st.metric("克朗巴赫α系数", f"{reliability_results['cronbach_alpha']:.4f}")
            
            # 信度水平判断
            alpha = reliability_results['cronbach_alpha']
            if alpha >= 0.9:
                reliability_level = "优秀"
                level_color = "🟢"
            elif alpha >= 0.8:
                reliability_level = "良好" 
                level_color = "🔵"
            elif alpha >= 0.7:
                reliability_level = "可接受"
                level_color = "🟡"
            else:
                reliability_level = "较差"
                level_color = "🔴"
            
            st.write(f"**信度水平:** {level_color} {reliability_level}")
            
            # 项目分析表
            if 'item_analysis' in reliability_results:
                st.write("##### 项目分析")
                st.dataframe(reliability_results['item_analysis'])
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '信度分析',
                'variables': selected_cols,
                'reliability_results': reliability_results
            }
            
            st.success("信度分析完成！")
            
        except Exception as e:
            st.error(f"信度分析失败: {str(e)}")


def execute_advanced_methods(analysis_option, processor, data):
    """执行进阶方法分析"""
    if analysis_option == "线性回归":
        execute_linear_regression(data)
    elif analysis_option == "逻辑回归":
        execute_logistic_regression(data)
    elif analysis_option == "聚类分析":
        execute_cluster_analysis(data)
    elif analysis_option == "因子分析":
        execute_factor_analysis(data)
    elif analysis_option == "主成分分析":
        execute_pca_analysis(data)
    elif analysis_option == "方差分析":
        execute_anova_analysis(data)


def execute_linear_regression(data):
    """线性回归分析"""
    st.write("#### 📈 线性回归分析")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 2:
        st.error("线性回归需要至少2个数值型变量")
        return
    
    # 选择因变量和自变量
    y_var = st.selectbox("选择因变量(Y)", numeric_cols)
    x_vars = st.multiselect("选择自变量(X)", [col for col in numeric_cols if col != y_var])
    
    if y_var and x_vars:
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score, mean_squared_error
        import numpy as np
        
        try:
            # 准备数据
            X = data[x_vars].dropna()
            y = data[y_var].dropna()
            
            # 确保X和y的索引一致
            common_index = X.index.intersection(y.index)
            X = X.loc[common_index]
            y = y.loc[common_index]
            
            # 拟合模型
            model = LinearRegression()
            model.fit(X, y)
            
            # 预测
            y_pred = model.predict(X)
            
            # 计算统计量
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            # 显示结果
            st.write("##### 回归分析结果")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("R²决定系数", f"{r2:.4f}")
            with col2:
                st.metric("RMSE", f"{rmse:.4f}")
            
            # 系数表
            coef_df = pd.DataFrame({
                '变量': ['常数项'] + x_vars,
                '系数': [model.intercept_] + model.coef_.tolist()
            })
            coef_df['系数'] = coef_df['系数'].round(4)
            
            st.write("##### 回归系数")
            st.dataframe(coef_df)
            
            # 回归方程
            equation_parts = [f"{model.intercept_:.4f}"]
            for var, coef in zip(x_vars, model.coef_):
                sign = "+" if coef >= 0 else ""
                equation_parts.append(f"{sign}{coef:.4f}*{var}")
            
            equation = f"{y_var} = " + " ".join(equation_parts)
            st.write("##### 回归方程")
            st.code(equation)
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '线性回归',
                'dependent_var': y_var,
                'independent_vars': x_vars,
                'r2_score': r2,
                'rmse': rmse,
                'coefficients': coef_df,
                'equation': equation
            }
            
            st.success("线性回归分析完成！")
            
        except Exception as e:
            st.error(f"回归分析失败: {str(e)}")


def execute_machine_learning(analysis_option, processor, data):
    """执行机器学习分析"""
    st.write(f"#### 🤖 {analysis_option}")
    st.info("机器学习模块正在开发中，敬请期待！")


def execute_time_series(analysis_option, processor, data):
    """执行时间序列分析"""
    st.write(f"#### 📊 {analysis_option}")
    st.info("时间序列分析模块正在开发中，敬请期待！")


def display_analysis_results():
    """显示分析结果"""
    if 'analysis_results' not in st.session_state:
        return
    
    results = st.session_state.analysis_results
    
    st.write("### 📋 分析结果摘要")
    st.write(f"**分析类型:** {results['type']}")
    
    if results['type'] == '频数分析':
        st.write(f"**分析变量:** {results['variable']}")
        st.dataframe(results['frequency_table'])
    
    elif results['type'] == '描述统计':
        st.write(f"**分析变量:** {', '.join(results['variables'])}")
        st.dataframe(results['descriptive_stats'])
    
    elif results['type'] == '信度分析':
        st.write(f"**量表变量:** {', '.join(results['variables'])}")
        st.metric("克朗巴赫α系数", f"{results['reliability_results']['cronbach_alpha']:.4f}")
    
    elif results['type'] == '线性回归':
        st.write(f"**因变量:** {results['dependent_var']}")
        st.write(f"**自变量:** {', '.join(results['independent_vars'])}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("R²", f"{results['r2_score']:.4f}")
        with col2:
            st.metric("RMSE", f"{results['rmse']:.4f}")


# 辅助函数实现
def execute_data_encoding(processor, data):
    """数据编码"""
    st.write("#### 🔢 数据编码")
    st.info("数据编码功能正在开发中...")


def execute_variable_generation(processor, data):
    """生成变量"""
    st.write("#### ➕ 生成变量")
    st.info("变量生成功能正在开发中...")


def execute_data_labeling(processor, data):
    """数据标签设置"""
    st.write("#### 🏷️ 数据标签设置")
    st.info("数据标签功能正在开发中...")


def execute_crosstab_analysis(data):
    """交叉分析(卡方检验)"""
    st.write("#### � 交叉分析(卡方检验)")
    
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    if len(categorical_cols) < 2:
        st.error("交叉分析需要至少2个分类变量")
        return
    
    # 选择分析变量
    col1, col2 = st.columns(2)
    with col1:
        var1 = st.selectbox("选择行变量", categorical_cols)
    with col2:
        remaining_cols = [col for col in categorical_cols if col != var1]
        var2 = st.selectbox("选择列变量", remaining_cols)
    
    # 分析参数
    alpha = st.selectbox("显著性水平", [0.05, 0.01, 0.001], index=0)
    
    if st.button("执行交叉分析"):
        try:
            from scipy.stats import chi2_contingency
            from scipy.stats.contingency import expected_freq
            
            # 创建交叉表
            crosstab = pd.crosstab(data[var1], data[var2], margins=True)
            
            # 移除边际总计进行卡方检验
            observed = crosstab.iloc[:-1, :-1]
            
            # 执行卡方检验
            chi2, p_value, dof, expected = chi2_contingency(observed)
            
            # 计算效应量 (Cramér's V)
            n = observed.sum().sum()
            cramers_v = np.sqrt(chi2 / (n * (min(observed.shape) - 1)))
            
            # 显示交叉表
            st.write("##### 频数交叉表")
            st.dataframe(crosstab)
            
            # 显示期望频数
            st.write("##### 期望频数")
            expected_df = pd.DataFrame(expected, 
                                     columns=observed.columns, 
                                     index=observed.index)
            st.dataframe(expected_df.round(2))
            
            # 显示百分比交叉表
            st.write("##### 百分比交叉表")
            percent_tab = pd.crosstab(data[var1], data[var2], normalize='index') * 100
            st.dataframe(percent_tab.round(2))
            
            # 统计检验结果
            st.write("##### 卡方检验结果")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("卡方值", f"{chi2:.4f}")
            with col2:
                st.metric("自由度", dof)
            with col3:
                st.metric("p值", f"{p_value:.4f}")
            with col4:
                st.metric("Cramér's V", f"{cramers_v:.4f}")
            
            # 结果解释
            significance = "显著" if p_value <= alpha else "不显著"
            effect_size = "大" if cramers_v >= 0.5 else "中" if cramers_v >= 0.3 else "小"
            
            st.write("##### 结果解释")
            st.write(f"- **统计显著性**: {significance} (α = {alpha})")
            st.write(f"- **效应量**: {effect_size} (Cramér's V = {cramers_v:.4f})")
            
            if p_value <= alpha:
                st.success(f"{var1} 和 {var2} 之间存在显著关联")
            else:
                st.info(f"{var1} 和 {var2} 之间无显著关联")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '交叉分析',
                'variables': [var1, var2],
                'crosstab': crosstab,
                'chi2': chi2,
                'p_value': p_value,
                'dof': dof,
                'cramers_v': cramers_v,
                'significance': significance
            }
            
            st.success("交叉分析完成！")
            
        except Exception as e:
            st.error(f"交叉分析失败: {str(e)}")


def execute_correlation_analysis(data):
    """相关分析"""
    st.write("#### 🔗 相关分析")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 2:
        st.error("相关分析需要至少2个数值型变量")
        return
    
    # 选择分析变量
    selected_cols = st.multiselect(
        "选择要分析的数值变量", 
        numeric_cols,
        default=numeric_cols[:min(8, len(numeric_cols))],
        help="选择用于相关分析的变量"
    )
    
    if len(selected_cols) < 2:
        st.warning("请至少选择2个变量进行相关分析")
        return
    
    # 相关分析参数
    col1, col2 = st.columns(2)
    with col1:
        method = st.selectbox("相关系数类型", ["Pearson", "Spearman", "Kendall"])
        alpha = st.selectbox("显著性水平", [0.05, 0.01, 0.001], index=0)
    
    with col2:
        min_corr = st.slider("最小相关系数阈值", 0.0, 1.0, 0.3, 0.1)
        show_pvalues = st.checkbox("显示p值", value=True)
    
    if st.button("执行相关分析"):
        try:
            import seaborn as sns
            import matplotlib.pyplot as plt
            from scipy.stats import pearsonr, spearmanr, kendalltau
            
            # 计算相关系数矩阵
            corr_data = data[selected_cols].dropna()
            
            if method == "Pearson":
                corr_matrix = corr_data.corr(method='pearson')
            elif method == "Spearman":
                corr_matrix = corr_data.corr(method='spearman')
            else:  # Kendall
                corr_matrix = corr_data.corr(method='kendall')
            
            # 计算p值矩阵
            n = len(selected_cols)
            p_matrix = np.zeros((n, n))
            
            for i, col1 in enumerate(selected_cols):
                for j, col2 in enumerate(selected_cols):
                    if i != j:
                        x = corr_data[col1].dropna()
                        y = corr_data[col2].dropna()
                        # 确保两个变量有相同的索引
                        common_idx = x.index.intersection(y.index)
                        x = x.loc[common_idx]
                        y = y.loc[common_idx]
                        
                        if len(x) > 2:
                            if method == "Pearson":
                                _, p_val = pearsonr(x, y)
                            elif method == "Spearman":
                                _, p_val = spearmanr(x, y)
                            else:  # Kendall
                                _, p_val = kendalltau(x, y)
                            p_matrix[i, j] = p_val
                        else:
                            p_matrix[i, j] = 1.0
                    else:
                        p_matrix[i, j] = 0.0
            
            # 显示相关系数矩阵
            st.write("##### 相关系数矩阵")
            
            # 创建热力图
            fig, ax = plt.subplots(figsize=(10, 8))
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=.5, cbar_kws={"shrink": .5}, ax=ax)
            ax.set_title(f'{method}相关系数热力图')
            st.pyplot(fig)
            plt.close(fig)
            
            # 显示数值结果
            st.dataframe(corr_matrix.round(3))
            
            if show_pvalues:
                st.write("##### p值矩阵")
                p_df = pd.DataFrame(p_matrix, columns=selected_cols, index=selected_cols)
                st.dataframe(p_df.round(4))
            
            # 强相关关系识别
            st.write("##### 强相关关系识别")
            strong_correlations = []
            
            for i in range(len(selected_cols)):
                for j in range(i+1, len(selected_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    p_val = p_matrix[i, j]
                    
                    if abs(corr_val) >= min_corr and p_val <= alpha:
                        strong_correlations.append({
                            '变量1': selected_cols[i],
                            '变量2': selected_cols[j],
                            '相关系数': round(corr_val, 4),
                            'p值': round(p_val, 4),
                            '相关强度': '强' if abs(corr_val) >= 0.7 else '中' if abs(corr_val) >= 0.5 else '弱',
                            '显著性': '***' if p_val <= 0.001 else '**' if p_val <= 0.01 else '*' if p_val <= 0.05 else 'ns'
                        })
            
            if strong_correlations:
                strong_df = pd.DataFrame(strong_correlations)
                st.dataframe(strong_df)
                st.info(f"发现 {len(strong_correlations)} 对显著相关关系")
            else:
                st.info("在当前阈值下未发现显著相关关系")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '相关分析',
                'method': method,
                'variables': selected_cols,
                'correlation_matrix': corr_matrix,
                'p_values': p_df if show_pvalues else None,
                'strong_correlations': strong_correlations,
                'n_samples': len(corr_data)
            }
            
            st.success("相关分析完成！")
            
        except Exception as e:
            st.error(f"相关分析失败: {str(e)}")


def execute_independent_ttest(data):
    """独立样本t检验"""
    st.write("#### � 独立样本t检验")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not numeric_cols or not categorical_cols:
        st.error("t检验需要至少一个数值型变量和一个分类变量")
        return
    
    # 选择变量
    col1, col2 = st.columns(2)
    with col1:
        dependent_var = st.selectbox("选择因变量(数值型)", numeric_cols)
    with col2:
        # 过滤只有2个唯一值的分类变量
        valid_cats = []
        for col in categorical_cols:
            unique_vals = data[col].dropna().nunique()
            if unique_vals == 2:
                valid_cats.append(col)
        
        if not valid_cats:
            st.error("需要一个只有两个类别的分组变量")
            return
            
        group_var = st.selectbox("选择分组变量(2类别)", valid_cats)
    
    # 检验参数
    alpha = st.selectbox("显著性水平", [0.05, 0.01, 0.001], index=0)
    equal_var = st.checkbox("假设方差相等", value=True)
    
    if st.button("执行t检验"):
        try:
            from scipy.stats import ttest_ind, levene
            from scipy import stats
            
            # 准备数据
            clean_data = data[[dependent_var, group_var]].dropna()
            groups = clean_data[group_var].unique()
            
            group1_data = clean_data[clean_data[group_var] == groups[0]][dependent_var]
            group2_data = clean_data[clean_data[group_var] == groups[1]][dependent_var]
            
            # 描述统计
            st.write("##### 组间描述统计")
            desc_stats = pd.DataFrame({
                '组别': [str(groups[0]), str(groups[1])],
                '样本量': [len(group1_data), len(group2_data)],
                '均值': [group1_data.mean(), group2_data.mean()],
                '标准差': [group1_data.std(), group2_data.std()],
                '标准误': [group1_data.sem(), group2_data.sem()],
                '最小值': [group1_data.min(), group2_data.min()],
                '最大值': [group1_data.max(), group2_data.max()]
            })
            st.dataframe(desc_stats.round(4))
            
            # 方差齐性检验 (Levene's test)
            levene_stat, levene_p = levene(group1_data, group2_data)
            
            st.write("##### 方差齐性检验 (Levene)")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Levene统计量", f"{levene_stat:.4f}")
            with col2:
                st.metric("p值", f"{levene_p:.4f}")
            
            if levene_p <= 0.05:
                st.warning("⚠️ 方差不齐 (p ≤ 0.05)，建议使用Welch t检验")
                equal_var = False
            else:
                st.success("✅ 方差齐性假设成立 (p > 0.05)")
            
            # 执行t检验
            t_stat, p_value = ttest_ind(group1_data, group2_data, equal_var=equal_var)
            
            # 计算效应量 (Cohen's d)
            pooled_std = np.sqrt(((len(group1_data) - 1) * group1_data.var() + 
                                 (len(group2_data) - 1) * group2_data.var()) / 
                                (len(group1_data) + len(group2_data) - 2))
            cohens_d = (group1_data.mean() - group2_data.mean()) / pooled_std
            
            # 自由度
            if equal_var:
                df = len(group1_data) + len(group2_data) - 2
            else:
                # Welch-Satterthwaite方程
                s1, s2 = group1_data.var(), group2_data.var()
                n1, n2 = len(group1_data), len(group2_data)
                df = (s1/n1 + s2/n2)**2 / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))
            
            # 显示t检验结果
            st.write("##### t检验结果")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("t统计量", f"{t_stat:.4f}")
            with col2:
                st.metric("自由度", f"{df:.1f}")
            with col3:
                st.metric("p值", f"{p_value:.4f}")
            with col4:
                st.metric("Cohen's d", f"{cohens_d:.4f}")
            
            # 结果解释
            significance = "显著" if p_value <= alpha else "不显著"
            effect_size = "大" if abs(cohens_d) >= 0.8 else "中" if abs(cohens_d) >= 0.5 else "小"
            
            st.write("##### 结果解释")
            st.write(f"- **统计显著性**: {significance} (α = {alpha})")
            st.write(f"- **效应量**: {effect_size} (|Cohen's d| = {abs(cohens_d):.4f})")
            st.write(f"- **检验类型**: {'Student t检验' if equal_var else 'Welch t检验'}")
            
            if p_value <= alpha:
                st.success(f"两组在{dependent_var}上存在显著差异")
            else:
                st.info(f"两组在{dependent_var}上无显著差异")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '独立样本t检验',
                'dependent_variable': dependent_var,
                'group_variable': group_var,
                'groups': groups.tolist(),
                't_statistic': t_stat,
                'p_value': p_value,
                'degrees_of_freedom': df,
                'cohens_d': cohens_d,
                'equal_var': equal_var,
                'levene_p': levene_p,
                'significance': significance
            }
            
            st.success("t检验完成！")
            
        except Exception as e:
            st.error(f"t检验失败: {str(e)}")


def execute_paired_ttest(data):
    """配对样本t检验"""
    st.write("#### � 配对样本t检验")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.error("配对t检验需要至少2个数值型变量")
        return
    
    # 选择配对变量
    col1, col2 = st.columns(2)
    with col1:
        var1 = st.selectbox("选择变量1", numeric_cols)
    with col2:
        remaining_vars = [col for col in numeric_cols if col != var1]
        var2 = st.selectbox("选择变量2", remaining_vars)
    
    # 检验参数
    alpha = st.selectbox("显著性水平", [0.05, 0.01, 0.001], index=0)
    
    if st.button("执行配对t检验"):
        try:
            from scipy.stats import ttest_rel, shapiro
            
            # 准备数据
            paired_data = data[[var1, var2]].dropna()
            
            if len(paired_data) < 3:
                st.error("配对数据太少，无法进行检验")
                return
            
            # 计算差值
            diff = paired_data[var1] - paired_data[var2]
            
            # 描述统计
            st.write("##### 配对样本描述统计")
            desc_stats = pd.DataFrame({
                '变量': [var1, var2, '差值'],
                '样本量': [len(paired_data[var1]), len(paired_data[var2]), len(diff)],
                '均值': [paired_data[var1].mean(), paired_data[var2].mean(), diff.mean()],
                '标准差': [paired_data[var1].std(), paired_data[var2].std(), diff.std()],
                '标准误': [paired_data[var1].sem(), paired_data[var2].sem(), diff.sem()],
                '最小值': [paired_data[var1].min(), paired_data[var2].min(), diff.min()],
                '最大值': [paired_data[var1].max(), paired_data[var2].max(), diff.max()]
            })
            st.dataframe(desc_stats.round(4))
            
            # 正态性检验（针对差值）
            if len(diff) >= 3:
                shapiro_stat, shapiro_p = shapiro(diff)
                
                st.write("##### 差值正态性检验 (Shapiro-Wilk)")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("W统计量", f"{shapiro_stat:.4f}")
                with col2:
                    st.metric("p值", f"{shapiro_p:.4f}")
                
                if shapiro_p <= 0.05:
                    st.warning("⚠️ 差值不符合正态分布 (p ≤ 0.05)，结果需谨慎解释")
                else:
                    st.success("✅ 差值符合正态分布假设 (p > 0.05)")
            
            # 执行配对t检验
            t_stat, p_value = ttest_rel(paired_data[var1], paired_data[var2])
            
            # 计算效应量 (Cohen's d for paired samples)
            cohens_d = diff.mean() / diff.std()
            
            # 自由度
            df = len(paired_data) - 1
            
            # 95%置信区间
            from scipy.stats import t as t_dist
            ci_margin = t_dist.ppf(0.975, df) * diff.sem()
            ci_lower = diff.mean() - ci_margin
            ci_upper = diff.mean() + ci_margin
            
            # 显示t检验结果
            st.write("##### 配对t检验结果")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("t统计量", f"{t_stat:.4f}")
            with col2:
                st.metric("自由度", df)
            with col3:
                st.metric("p值", f"{p_value:.4f}")
            with col4:
                st.metric("Cohen's d", f"{cohens_d:.4f}")
            
            # 差值的置信区间
            st.write("##### 差值的95%置信区间")
            st.write(f"[{ci_lower:.4f}, {ci_upper:.4f}]")
            
            # 结果解释
            significance = "显著" if p_value <= alpha else "不显著"
            effect_size = "大" if abs(cohens_d) >= 0.8 else "中" if abs(cohens_d) >= 0.5 else "小"
            
            st.write("##### 结果解释")
            st.write(f"- **统计显著性**: {significance} (α = {alpha})")
            st.write(f"- **效应量**: {effect_size} (|Cohen's d| = {abs(cohens_d):.4f})")
            st.write(f"- **平均差值**: {diff.mean():.4f}")
            
            if p_value <= alpha:
                direction = "显著增加" if diff.mean() > 0 else "显著减少"
                st.success(f"从{var2}到{var1}{direction}")
            else:
                st.info(f"{var1}和{var2}之间无显著差异")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '配对样本t检验',
                'variable1': var1,
                'variable2': var2,
                't_statistic': t_stat,
                'p_value': p_value,
                'degrees_of_freedom': df,
                'cohens_d': cohens_d,
                'mean_difference': diff.mean(),
                'confidence_interval': [ci_lower, ci_upper],
                'shapiro_p': shapiro_p if len(diff) >= 3 else None,
                'significance': significance
            }
            
            st.success("配对t检验完成！")
            
        except Exception as e:
            st.error(f"配对t检验失败: {str(e)}")


def execute_validity_analysis(processor, data):
    """效度分析"""
    st.write("#### 📝 效度分析")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 3:
        st.error("效度分析需要至少3个数值型变量")
        return
    
    # 选择分析变量
    selected_cols = st.multiselect(
        "选择用于效度分析的变量", 
        numeric_cols,
        default=numeric_cols[:min(10, len(numeric_cols))],
        help="选择用于效度分析的数值型变量"
    )
    
    if len(selected_cols) < 3:
        st.warning("请至少选择3个变量进行效度分析")
        return
    
    # 效度分析类型
    validity_type = st.selectbox(
        "选择效度分析类型",
        ["内容效度", "结构效度(探索性因子分析)", "聚合效度", "区分效度"]
    )
    
    if st.button("执行效度分析"):
        try:
            import numpy as np
            from sklearn.decomposition import PCA, FactorAnalysis
            from factor_analyzer import FactorAnalyzer
            from scipy.stats import pearsonr
            
            # 准备数据
            validity_data = data[selected_cols].dropna()
            
            if validity_type == "内容效度":
                st.write("##### 内容效度分析")
                st.info("内容效度主要通过专家判断进行评估，此处提供相关统计信息：")
                
                # 变量描述统计
                desc_stats = validity_data.describe()
                st.dataframe(desc_stats.round(4))
                
                # 变量间相关性
                corr_matrix = validity_data.corr()
                
                import matplotlib.pyplot as plt
                import seaborn as sns
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
                ax.set_title('变量间相关系数矩阵')
                st.pyplot(fig)
                plt.close(fig)
                
            elif validity_type == "结构效度(探索性因子分析)":
                st.write("##### 结构效度 - 探索性因子分析(EFA)")
                
                # 数据适用性检验
                from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
                
                # Bartlett's检验
                chi_square_value, p_value = calculate_bartlett_sphericity(validity_data)
                st.write("**Bartlett球形检验:**")
                st.write(f"- 卡方值: {chi_square_value:.4f}")
                st.write(f"- p值: {p_value:.4f}")
                
                if p_value < 0.05:
                    st.success("✅ Bartlett检验显著，数据适合因子分析")
                else:
                    st.warning("⚠️ Bartlett检验不显著，数据可能不适合因子分析")
                
                # KMO检验
                kmo_all, kmo_model = calculate_kmo(validity_data)
                st.write("**KMO采样适度量检验:**")
                st.write(f"- 总体KMO值: {kmo_model:.4f}")
                
                if kmo_model >= 0.8:
                    st.success("✅ KMO > 0.8，非常适合因子分析")
                elif kmo_model >= 0.7:
                    st.success("✅ KMO > 0.7，适合因子分析")
                elif kmo_model >= 0.6:
                    st.info("ℹ️ KMO > 0.6，勉强适合因子分析")
                else:
                    st.warning("⚠️ KMO < 0.6，不适合因子分析")
                
                # 因子数量选择
                n_factors = st.slider("选择因子数量", 1, min(len(selected_cols)-1, 8), 2)
                
                # 执行因子分析
                fa = FactorAnalyzer(n_factors=n_factors, rotation='varimax')
                fa.fit(validity_data)
                
                # 因子载荷矩阵
                loadings = fa.loadings_
                loadings_df = pd.DataFrame(loadings, 
                                         columns=[f'因子{i+1}' for i in range(n_factors)],
                                         index=selected_cols)
                
                st.write("**因子载荷矩阵:**")
                st.dataframe(loadings_df.round(4))
                
                # 特征值
                eigenvalues = fa.get_eigenvalues()[0]
                st.write("**特征值:**")
                eigenvalue_df = pd.DataFrame({
                    '因子': [f'因子{i+1}' for i in range(len(eigenvalues))],
                    '特征值': eigenvalues,
                    '方差贡献率(%)': eigenvalues / len(selected_cols) * 100,
                    '累积贡献率(%)': np.cumsum(eigenvalues) / len(selected_cols) * 100
                })
                st.dataframe(eigenvalue_df.round(4))
                
                # 碎石图
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(range(1, len(eigenvalues)+1), eigenvalues, 'bo-')
                ax.axhline(y=1, color='r', linestyle='--', label='特征值=1')
                ax.set_xlabel('因子序号')
                ax.set_ylabel('特征值')
                ax.set_title('碎石图')
                ax.legend()
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
                plt.close(fig)
                
            elif validity_type == "聚合效度":
                st.write("##### 聚合效度分析")
                
                # 计算平均方差提取量(AVE)和组合信度(CR)
                # 假设所有变量属于同一构念
                corr_matrix = validity_data.corr()
                
                # 计算Cronbach's Alpha
                n_items = len(selected_cols)
                item_variances = validity_data.var()
                total_variance = validity_data.sum(axis=1).var()
                
                alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
                
                st.write(f"**Cronbach's α系数**: {alpha:.4f}")
                
                if alpha >= 0.9:
                    st.success("✅ α ≥ 0.9，内部一致性非常好")
                elif alpha >= 0.8:
                    st.success("✅ α ≥ 0.8，内部一致性良好")
                elif alpha >= 0.7:
                    st.info("ℹ️ α ≥ 0.7，内部一致性可接受")
                else:
                    st.warning("⚠️ α < 0.7，内部一致性较差")
                
                # 项目-总分相关
                st.write("**项目-总分相关分析:**")
                total_score = validity_data.sum(axis=1)
                item_total_corr = []
                
                for col in selected_cols:
                    corr, p_val = pearsonr(validity_data[col], total_score - validity_data[col])
                    item_total_corr.append({
                        '项目': col,
                        '项目-总分相关': corr,
                        'p值': p_val,
                        '删除该项目后的α': np.nan  # 可以进一步计算
                    })
                
                item_corr_df = pd.DataFrame(item_total_corr)
                st.dataframe(item_corr_df.round(4))
                
            elif validity_type == "区分效度":
                st.write("##### 区分效度分析")
                
                # 计算变量间相关系数
                corr_matrix = validity_data.corr()
                
                st.write("**变量间相关系数矩阵:**")
                st.dataframe(corr_matrix.round(4))
                
                # 识别高相关项目（可能缺乏区分效度）
                high_corr_pairs = []
                threshold = 0.8
                
                for i in range(len(selected_cols)):
                    for j in range(i+1, len(selected_cols)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) >= threshold:
                            high_corr_pairs.append({
                                '变量1': selected_cols[i],
                                '变量2': selected_cols[j],
                                '相关系数': corr_val
                            })
                
                if high_corr_pairs:
                    st.write(f"**高相关变量对 (|r| ≥ {threshold}):**")
                    high_corr_df = pd.DataFrame(high_corr_pairs)
                    st.dataframe(high_corr_df.round(4))
                    st.warning("⚠️ 以上变量对相关过高，可能缺乏区分效度")
                else:
                    st.success("✅ 未发现高相关变量对，区分效度良好")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '效度分析',
                'validity_type': validity_type,
                'variables': selected_cols,
                'sample_size': len(validity_data)
            }
            
            st.success("效度分析完成！")
            
        except Exception as e:
            st.error(f"效度分析失败: {str(e)}")


def execute_multiple_choice_analysis(data):
    """多选题分析"""
    st.write("#### ☑️ 多选题分析")
    
    # 获取所有列
    all_cols = data.columns.tolist()
    
    # 选择多选题相关列
    st.write("##### 选择多选题变量")
    selected_cols = st.multiselect(
        "选择多选题的各个选项变量",
        all_cols,
        help="选择代表多选题各个选项的变量（通常为0/1编码或是/否）"
    )
    
    if len(selected_cols) < 2:
        st.warning("请至少选择2个多选题选项变量")
        return
    
    # 多选题分析参数
    col1, col2 = st.columns(2)
    with col1:
        value_type = st.selectbox("数据编码类型", ["0/1编码", "是/否", "True/False", "自定义"])
        show_combination = st.checkbox("显示选项组合分析", value=True)
    
    with col2:
        if value_type == "自定义":
            positive_value = st.text_input("正向值（选中）", "1")
            negative_value = st.text_input("负向值（未选中）", "0")
        else:
            positive_value = {"0/1编码": "1", "是/否": "是", "True/False": "True"}[value_type]
            negative_value = {"0/1编码": "0", "是/否": "否", "True/False": "False"}[value_type]
    
    if st.button("执行多选题分析"):
        try:
            # 准备数据
            multi_data = data[selected_cols].copy()
            
            # 转换为统一的0/1编码
            for col in selected_cols:
                multi_data[col] = (multi_data[col].astype(str) == str(positive_value)).astype(int)
            
            # 基本统计
            st.write("##### 各选项选择情况")
            
            option_stats = []
            total_responses = len(multi_data)
            
            for col in selected_cols:
                selected_count = multi_data[col].sum()
                percentage = (selected_count / total_responses) * 100
                
                option_stats.append({
                    '选项': col,
                    '选择人数': selected_count,
                    '选择率(%)': percentage,
                    '未选择人数': total_responses - selected_count,
                    '未选择率(%)': 100 - percentage
                })
            
            stats_df = pd.DataFrame(option_stats)
            st.dataframe(stats_df.round(2))
            
            # 可视化选择率
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 6))
            
            bars = ax.bar(stats_df['选项'], stats_df['选择率(%)'])
            ax.set_xlabel('选项')
            ax.set_ylabel('选择率 (%)')
            ax.set_title('各选项选择率')
            ax.tick_params(axis='x', rotation=45)
            
            # 在柱状图上显示数值
            for bar, percentage in zip(bars, stats_df['选择率(%)']):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{percentage:.1f}%', ha='center', va='bottom')
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            
            # 选项组合分析
            if show_combination:
                st.write("##### 选项组合分析")
                
                # 计算每个人选择的选项数量
                multi_data['total_selected'] = multi_data[selected_cols].sum(axis=1)
                
                # 选择数量分布
                selection_counts = multi_data['total_selected'].value_counts().sort_index()
                
                st.write("**选择数量分布:**")
                count_stats = pd.DataFrame({
                    '选择数量': selection_counts.index,
                    '人数': selection_counts.values,
                    '比例(%)': (selection_counts.values / total_responses) * 100
                })
                st.dataframe(count_stats.round(2))
                
                # 选择数量分布图
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(count_stats['选择数量'], count_stats['比例(%)'])
                ax.set_xlabel('选择数量')
                ax.set_ylabel('比例 (%)')
                ax.set_title('选择数量分布')
                st.pyplot(fig)
                plt.close(fig)
                
                # 选项共现分析
                if len(selected_cols) <= 10:  # 避免组合过多
                    st.write("**选项共现矩阵:**")
                    
                    # 计算选项间的共现次数
                    cooccurrence = np.zeros((len(selected_cols), len(selected_cols)))
                    
                    for i, col1 in enumerate(selected_cols):
                        for j, col2 in enumerate(selected_cols):
                            if i != j:
                                # 计算同时选择两个选项的人数
                                cooccurrence[i, j] = ((multi_data[col1] == 1) & (multi_data[col2] == 1)).sum()
                            else:
                                cooccurrence[i, j] = multi_data[col1].sum()
                    
                    cooccur_df = pd.DataFrame(cooccurrence, 
                                            columns=selected_cols, 
                                            index=selected_cols)
                    st.dataframe(cooccur_df.astype(int))
                    
                    # 共现热力图
                    import seaborn as sns
                    fig, ax = plt.subplots(figsize=(10, 8))
                    sns.heatmap(cooccur_df, annot=True, fmt='d', cmap='Blues', ax=ax)
                    ax.set_title('选项共现热力图')
                    st.pyplot(fig)
                    plt.close(fig)
                
                # 最常见的选项组合
                st.write("**最常见的选项组合 (Top 10):**")
                
                # 创建组合模式
                multi_data['pattern'] = multi_data[selected_cols].apply(
                    lambda row: '+'.join([col for col, val in row.items() if col in selected_cols and val == 1]),
                    axis=1
                )
                
                pattern_counts = multi_data['pattern'].value_counts().head(10)
                
                pattern_stats = pd.DataFrame({
                    '选项组合': pattern_counts.index,
                    '出现次数': pattern_counts.values,
                    '比例(%)': (pattern_counts.values / total_responses) * 100
                })
                
                # 处理空组合
                pattern_stats['选项组合'] = pattern_stats['选项组合'].replace('', '(未选择任何选项)')
                
                st.dataframe(pattern_stats.round(2))
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '多选题分析',
                'variables': selected_cols,
                'total_responses': total_responses,
                'option_stats': stats_df.to_dict('records'),
                'selection_distribution': count_stats.to_dict('records') if show_combination else None
            }
            
            st.success("多选题分析完成！")
            
        except Exception as e:
            st.error(f"多选题分析失败: {str(e)}")


def execute_questionnaire_quality(data):
    """问卷质量评估"""
    st.write("#### 📋 问卷质量评估")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 3:
        st.error("问卷质量评估需要至少3个数值型变量")
        return
    
    # 选择问卷题目变量
    selected_cols = st.multiselect(
        "选择问卷题目变量",
        numeric_cols,
        default=numeric_cols[:min(20, len(numeric_cols))],
        help="选择代表问卷题目的数值型变量"
    )
    
    if len(selected_cols) < 3:
        st.warning("请至少选择3个问卷题目变量")
        return
    
    # 评估参数
    col1, col2 = st.columns(2)
    with col1:
        scale_type = st.selectbox("量表类型", ["Likert量表", "语义差异量表", "其他"])
        if scale_type == "Likert量表":
            scale_range = st.selectbox("量表范围", ["1-5", "1-7", "1-10", "自定义"])
            if scale_range == "自定义":
                min_val = st.number_input("最小值", value=1)
                max_val = st.number_input("最大值", value=5)
            else:
                min_val, max_val = map(int, scale_range.split('-'))
    
    with col2:
        check_outliers = st.checkbox("检查异常值", value=True)
        check_missing = st.checkbox("检查缺失值模式", value=True)
    
    if st.button("执行问卷质量评估"):
        try:
            # 准备数据
            quality_data = data[selected_cols].copy()
            
            st.write("##### 📊 基本数据质量")
            
            # 1. 基本统计信息
            basic_stats = []
            total_responses = len(quality_data)
            
            for col in selected_cols:
                col_data = quality_data[col]
                
                basic_stats.append({
                    '题目': col,
                    '有效回答数': col_data.count(),
                    '缺失值数': col_data.isnull().sum(),
                    '缺失率(%)': (col_data.isnull().sum() / total_responses) * 100,
                    '均值': col_data.mean(),
                    '标准差': col_data.std(),
                    '最小值': col_data.min(),
                    '最大值': col_data.max()
                })
            
            basic_df = pd.DataFrame(basic_stats)
            st.dataframe(basic_df.round(4))
            
            # 2. 缺失值模式分析
            if check_missing:
                st.write("##### 📝 缺失值模式分析")
                
                missing_pattern = quality_data.isnull().sum()
                if missing_pattern.sum() > 0:
                    st.write("**各题目缺失值统计:**")
                    missing_df = pd.DataFrame({
                        '题目': missing_pattern.index,
                        '缺失值数': missing_pattern.values,
                        '缺失率(%)': (missing_pattern.values / total_responses) * 100
                    })
                    st.dataframe(missing_df.round(2))
                    
                    # 缺失值可视化
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(12, 6))
                    bars = ax.bar(missing_df['题目'], missing_df['缺失率(%)'])
                    ax.set_xlabel('题目')
                    ax.set_ylabel('缺失率 (%)')
                    ax.set_title('各题目缺失率')
                    ax.tick_params(axis='x', rotation=45)
                    
                    # 标记高缺失率的题目
                    for bar, rate in zip(bars, missing_df['缺失率(%)']):
                        if rate > 10:  # 缺失率超过10%
                            bar.set_color('red')
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                   f'{rate:.1f}%', ha='center', va='bottom', color='red')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)
                    
                    # 缺失值建议
                    high_missing = missing_df[missing_df['缺失率(%)'] > 10]
                    if not high_missing.empty:
                        st.warning(f"⚠️ 以下题目缺失率超过10%，建议检查: {', '.join(high_missing['题目'].tolist())}")
                else:
                    st.success("✅ 所有题目都没有缺失值")
            
            # 3. 异常值检测
            if check_outliers:
                st.write("##### 🎯 异常值检测")
                
                # 如果是Likert量表，检查超出范围的值
                if scale_type == "Likert量表":
                    out_of_range = []
                    for col in selected_cols:
                        col_data = quality_data[col].dropna()
                        below_min = (col_data < min_val).sum()
                        above_max = (col_data > max_val).sum()
                        
                        if below_min > 0 or above_max > 0:
                            out_of_range.append({
                                '题目': col,
                                f'小于{min_val}的值': below_min,
                                f'大于{max_val}的值': above_max,
                                '异常值总数': below_min + above_max
                            })
                    
                    if out_of_range:
                        st.write("**超出量表范围的值:**")
                        out_range_df = pd.DataFrame(out_of_range)
                        st.dataframe(out_range_df)
                        st.warning("⚠️ 发现超出量表范围的异常值，建议检查数据录入")
                    else:
                        st.success("✅ 所有值都在量表范围内")
                
                # 使用IQR方法检测异常值
                outlier_stats = []
                for col in selected_cols:
                    col_data = quality_data[col].dropna()
                    if len(col_data) > 0:
                        Q1 = col_data.quantile(0.25)
                        Q3 = col_data.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        
                        outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                        
                        outlier_stats.append({
                            '题目': col,
                            '异常值数量': len(outliers),
                            '异常值比例(%)': (len(outliers) / len(col_data)) * 100,
                            '下界': lower_bound,
                            '上界': upper_bound
                        })
                
                outlier_df = pd.DataFrame(outlier_stats)
                st.write("**IQR方法异常值检测:**")
                st.dataframe(outlier_df.round(4))
            
            # 4. 反向题检测
            st.write("##### 🔄 反向题一致性检查")
            
            # 计算题目间相关系数
            corr_matrix = quality_data.corr()
            
            # 识别可能的反向题（与其他题目普遍负相关）
            negative_corr_items = []
            for col in selected_cols:
                col_corrs = corr_matrix[col].drop(col)  # 排除自相关
                avg_corr = col_corrs.mean()
                negative_corr_count = (col_corrs < 0).sum()
                
                if avg_corr < 0 or negative_corr_count > len(col_corrs) * 0.5:
                    negative_corr_items.append({
                        '题目': col,
                        '平均相关系数': avg_corr,
                        '负相关题目数': negative_corr_count,
                        '负相关比例(%)': (negative_corr_count / len(col_corrs)) * 100
                    })
            
            if negative_corr_items:
                st.write("**可能的反向题目:**")
                reverse_df = pd.DataFrame(negative_corr_items)
                st.dataframe(reverse_df.round(4))
                st.info("ℹ️ 以上题目可能为反向题，请检查是否需要反向编码")
            else:
                st.success("✅ 未发现明显的反向题目")
            
            # 5. 内部一致性评估
            st.write("##### 📈 内部一致性评估")
            
            # Cronbach's Alpha
            valid_data = quality_data.dropna()
            if len(valid_data) > 0 and len(selected_cols) > 1:
                n_items = len(selected_cols)
                item_variances = valid_data.var()
                total_variance = valid_data.sum(axis=1).var()
                
                if total_variance > 0:
                    alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Cronbach's α", f"{alpha:.4f}")
                    with col2:
                        st.metric("题目数量", n_items)
                    with col3:
                        st.metric("有效样本", len(valid_data))
                    
                    # Alpha解释
                    if alpha >= 0.9:
                        st.success("✅ α ≥ 0.9，内部一致性极佳")
                    elif alpha >= 0.8:
                        st.success("✅ α ≥ 0.8，内部一致性良好")
                    elif alpha >= 0.7:
                        st.info("ℹ️ α ≥ 0.7，内部一致性可接受")
                    elif alpha >= 0.6:
                        st.warning("⚠️ α ≥ 0.6，内部一致性较低")
                    else:
                        st.error("❌ α < 0.6，内部一致性差")
            
            # 6. 综合质量评分
            st.write("##### 🏆 综合质量评分")
            
            # 计算各维度得分
            missing_score = max(0, 100 - (missing_pattern.mean() / total_responses * 100 * 2))  # 缺失值越少分数越高
            consistency_score = min(100, alpha * 100) if 'alpha' in locals() else 50  # 内部一致性分数
            
            if check_outliers and outlier_df['异常值比例(%)'].mean() < 5:
                outlier_score = 90
            elif check_outliers and outlier_df['异常值比例(%)'].mean() < 10:
                outlier_score = 70
            else:
                outlier_score = 50
            
            overall_score = (missing_score + consistency_score + outlier_score) / 3
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("数据完整性", f"{missing_score:.1f}/100")
            with col2:
                st.metric("内部一致性", f"{consistency_score:.1f}/100")
            with col3:
                st.metric("数据质量", f"{outlier_score:.1f}/100")
            with col4:
                st.metric("综合评分", f"{overall_score:.1f}/100")
            
            # 质量等级
            if overall_score >= 90:
                st.success("🌟 问卷质量: 优秀")
            elif overall_score >= 80:
                st.success("✅ 问卷质量: 良好")
            elif overall_score >= 70:
                st.info("ℹ️ 问卷质量: 一般")
            elif overall_score >= 60:
                st.warning("⚠️ 问卷质量: 较差")
            else:
                st.error("❌ 问卷质量: 差")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '问卷质量评估',
                'variables': selected_cols,
                'total_responses': total_responses,
                'basic_stats': basic_df.to_dict('records'),
                'missing_rate': missing_pattern.mean() / total_responses * 100,
                'cronbach_alpha': alpha if 'alpha' in locals() else None,
                'overall_score': overall_score
            }
            
            st.success("问卷质量评估完成！")
            
        except Exception as e:
            st.error(f"问卷质量评估失败: {str(e)}")


def execute_logistic_regression(data):
    """逻辑回归分析"""
    st.write("#### 📈 逻辑回归分析")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not categorical_cols:
        st.error("逻辑回归需要至少一个分类型因变量")
        return
    
    # 选择变量
    col1, col2 = st.columns(2)
    with col1:
        # 只显示二分类变量作为因变量
        binary_vars = []
        for col in categorical_cols:
            if data[col].nunique() == 2:
                binary_vars.append(col)
        
        if not binary_vars:
            st.error("逻辑回归需要一个二分类因变量")
            return
            
        y_var = st.selectbox("选择因变量(二分类)", binary_vars)
    
    with col2:
        x_vars = st.multiselect("选择自变量", 
                               [col for col in numeric_cols if col != y_var],
                               help="选择数值型自变量")
    
    if not x_vars:
        st.warning("请至少选择一个自变量")
        return
    
    # 逻辑回归参数
    col1, col2 = st.columns(2)
    with col1:
        test_size = st.slider("测试集比例", 0.1, 0.5, 0.3)
        solver = st.selectbox("求解器", ["liblinear", "lbfgs", "newton-cg", "sag", "saga"])
    
    with col2:
        max_iter = st.number_input("最大迭代次数", 100, 10000, 1000)
        random_state = st.number_input("随机种子", 0, 1000, 42)
    
    if st.button("执行逻辑回归"):
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
            from sklearn.preprocessing import LabelEncoder
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 准备数据
            clean_data = data[[y_var] + x_vars].dropna()
            
            if len(clean_data) < 20:
                st.error("样本量太少，无法进行逻辑回归")
                return
            
            # 编码因变量
            le = LabelEncoder()
            y = le.fit_transform(clean_data[y_var])
            X = clean_data[x_vars]
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            # 拟合模型
            model = LogisticRegression(solver=solver, max_iter=max_iter, random_state=random_state)
            model.fit(X_train, y_train)
            
            # 预测
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # 显示结果
            st.write("##### 模型性能")
            
            # 基本指标
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            auc_score = roc_auc_score(y_test, y_pred_proba)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("训练集准确率", f"{train_score:.4f}")
            with col2:
                st.metric("测试集准确率", f"{test_score:.4f}")
            with col3:
                st.metric("AUC值", f"{auc_score:.4f}")
            
            # 回归系数
            st.write("##### 回归系数")
            coef_df = pd.DataFrame({
                '变量': ['常数项'] + x_vars,
                '系数': [model.intercept_[0]] + model.coef_[0].tolist(),
                '优势比(OR)': [np.exp(model.intercept_[0])] + [np.exp(coef) for coef in model.coef_[0]]
            })
            st.dataframe(coef_df.round(4))
            
            # 混淆矩阵
            st.write("##### 混淆矩阵")
            cm = confusion_matrix(y_test, y_pred)
            cm_df = pd.DataFrame(cm, 
                               columns=[f'预测_{label}' for label in le.classes_],
                               index=[f'实际_{label}' for label in le.classes_])
            st.dataframe(cm_df)
            
            # 分类报告
            st.write("##### 分类报告")
            report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)
            report_df = pd.DataFrame(report).transpose().round(4)
            st.dataframe(report_df)
            
            # ROC曲线
            st.write("##### ROC曲线")
            fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(fpr, tpr, label=f'ROC曲线 (AUC = {auc_score:.3f})')
            ax.plot([0, 1], [0, 1], 'k--', label='随机猜测')
            ax.set_xlabel('假正率 (FPR)')
            ax.set_ylabel('真正率 (TPR)')
            ax.set_title('ROC曲线')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)
            
            # 模型解释
            st.write("##### 模型解释")
            st.write("**系数解释:**")
            for var, coef, odds_ratio in zip(x_vars, model.coef_[0], [np.exp(c) for c in model.coef_[0]]):
                if coef > 0:
                    effect = "增加"
                    direction = "正向"
                else:
                    effect = "减少"
                    direction = "负向"
                
                st.write(f"- **{var}**: {direction}影响，系数={coef:.4f}，优势比={odds_ratio:.4f}")
                st.write(f"  {var}每增加1个单位，{y_var}的对数几比{effect}{abs(coef):.4f}")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '逻辑回归',
                'dependent_var': y_var,
                'independent_vars': x_vars,
                'train_accuracy': train_score,
                'test_accuracy': test_score,
                'auc_score': auc_score,
                'coefficients': coef_df.to_dict('records'),
                'confusion_matrix': cm.tolist(),
                'classification_report': report
            }
            
            st.success("逻辑回归分析完成！")
            
        except Exception as e:
            st.error(f"逻辑回归分析失败: {str(e)}")


def execute_machine_learning(analysis_option, processor, data):
    """执行机器学习分析"""
    st.write(f"#### 🤖 {analysis_option}")
    
    if analysis_option == "分类算法":
        execute_classification_algorithms(data)
    elif analysis_option == "回归算法":
        execute_regression_algorithms(data)
    elif analysis_option == "聚类算法":
        execute_clustering_algorithms(data)
    elif analysis_option == "降维算法":
        execute_dimensionality_reduction(data)
    elif analysis_option == "模型评估":
        execute_model_evaluation(data)
    else:
        st.info(f"{analysis_option}功能正在开发中...")


def execute_classification_algorithms(data):
    """分类算法"""
    st.write("##### 分类算法比较")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not categorical_cols or not numeric_cols:
        st.error("分类算法需要数值型特征和分类型目标变量")
        return
    
    # 选择变量
    col1, col2 = st.columns(2)
    with col1:
        target_var = st.selectbox("选择目标变量(分类)", categorical_cols)
    with col2:
        feature_vars = st.multiselect("选择特征变量", 
                                    [col for col in numeric_cols],
                                    default=numeric_cols[:min(5, len(numeric_cols))])
    
    if not feature_vars:
        st.warning("请选择至少一个特征变量")
        return
    
    # 算法选择
    algorithms = st.multiselect(
        "选择分类算法",
        ["随机森林", "支持向量机", "朴素贝叶斯", "K近邻", "决策树", "梯度提升"],
        default=["随机森林", "支持向量机", "朴素贝叶斯"]
    )
    
    if not algorithms:
        st.warning("请选择至少一个算法")
        return
    
    # 参数设置
    test_size = st.slider("测试集比例", 0.1, 0.5, 0.3)
    cv_folds = st.slider("交叉验证折数", 3, 10, 5)
    
    if st.button("执行分类算法比较"):
        try:
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.svm import SVC
            from sklearn.naive_bayes import GaussianNB
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.model_selection import train_test_split, cross_val_score
            from sklearn.preprocessing import LabelEncoder, StandardScaler
            from sklearn.metrics import classification_report, accuracy_score
            
            # 准备数据
            clean_data = data[feature_vars + [target_var]].dropna()
            
            if len(clean_data) < 20:
                st.error("样本量太少，无法进行机器学习")
                return
            
            # 编码目标变量
            le = LabelEncoder()
            y = le.fit_transform(clean_data[target_var])
            X = clean_data[feature_vars]
            
            # 标准化特征
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 划分数据集
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # 定义算法
            models = {}
            if "随机森林" in algorithms:
                models["随机森林"] = RandomForestClassifier(n_estimators=100, random_state=42)
            if "支持向量机" in algorithms:
                models["支持向量机"] = SVC(random_state=42)
            if "朴素贝叶斯" in algorithms:
                models["朴素贝叶斯"] = GaussianNB()
            if "K近邻" in algorithms:
                models["K近邻"] = KNeighborsClassifier(n_neighbors=5)
            if "决策树" in algorithms:
                models["决策树"] = DecisionTreeClassifier(random_state=42)
            if "梯度提升" in algorithms:
                models["梯度提升"] = GradientBoostingClassifier(random_state=42)
            
            # 训练和评估模型
            results = []
            
            st.write("##### 模型性能比较")
            
            for name, model in models.items():
                # 训练模型
                model.fit(X_train, y_train)
                
                # 预测
                y_pred = model.predict(X_test)
                
                # 计算指标
                train_score = model.score(X_train, y_train)
                test_score = accuracy_score(y_test, y_pred)
                cv_scores = cross_val_score(model, X_scaled, y, cv=cv_folds)
                
                results.append({
                    '算法': name,
                    '训练准确率': f"{train_score:.4f}",
                    '测试准确率': f"{test_score:.4f}",
                    '交叉验证均值': f"{cv_scores.mean():.4f}",
                    '交叉验证标准差': f"{cv_scores.std():.4f}"
                })
            
            results_df = pd.DataFrame(results)
            st.dataframe(results_df)
            
            # 找出最佳模型
            best_model_name = results_df.loc[results_df['测试准确率'].astype(float).idxmax(), '算法']
            st.success(f"🏆 最佳模型: {best_model_name}")
            
            # 特征重要性（如果支持）
            best_model = models[best_model_name]
            if hasattr(best_model, 'feature_importances_'):
                st.write("##### 特征重要性")
                importance_df = pd.DataFrame({
                    '特征': feature_vars,
                    '重要性': best_model.feature_importances_
                }).sort_values('重要性', ascending=False)
                
                st.dataframe(importance_df.round(4))
                
                # 特征重要性可视化
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.barh(importance_df['特征'], importance_df['重要性'])
                ax.set_xlabel('重要性')
                ax.set_title(f'{best_model_name} - 特征重要性')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '分类算法比较',
                'target_variable': target_var,
                'feature_variables': feature_vars,
                'algorithms': algorithms,
                'results': results_df.to_dict('records'),
                'best_model': best_model_name
            }
            
            st.success("分类算法比较完成！")
            
        except Exception as e:
            st.error(f"分类算法比较失败: {str(e)}")


def execute_regression_algorithms(data):
    """回归算法"""
    st.write("##### 回归算法比较")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.error("回归算法需要至少2个数值型变量")
        return
    
    # 选择变量
    col1, col2 = st.columns(2)
    with col1:
        target_var = st.selectbox("选择目标变量", numeric_cols)
    with col2:
        feature_vars = st.multiselect("选择特征变量", 
                                    [col for col in numeric_cols if col != target_var],
                                    default=[col for col in numeric_cols if col != target_var][:min(5, len(numeric_cols)-1)])
    
    if not feature_vars:
        st.warning("请选择至少一个特征变量")
        return
    
    # 算法选择
    algorithms = st.multiselect(
        "选择回归算法",
        ["线性回归", "随机森林回归", "支持向量回归", "决策树回归", "梯度提升回归", "岭回归"],
        default=["线性回归", "随机森林回归", "梯度提升回归"]
    )
    
    if not algorithms:
        st.warning("请选择至少一个算法")
        return
    
    # 参数设置
    test_size = st.slider("测试集比例", 0.1, 0.5, 0.3)
    cv_folds = st.slider("交叉验证折数", 3, 10, 5)
    
    if st.button("执行回归算法比较"):
        try:
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.svm import SVR
            from sklearn.tree import DecisionTreeRegressor
            from sklearn.linear_model import LinearRegression, Ridge
            from sklearn.model_selection import train_test_split, cross_val_score
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
            import numpy as np
            
            # 准备数据
            clean_data = data[feature_vars + [target_var]].dropna()
            
            if len(clean_data) < 20:
                st.error("样本量太少，无法进行机器学习")
                return
            
            X = clean_data[feature_vars]
            y = clean_data[target_var]
            
            # 标准化特征
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # 划分数据集
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=42
            )
            
            # 定义算法
            models = {}
            if "线性回归" in algorithms:
                models["线性回归"] = LinearRegression()
            if "随机森林回归" in algorithms:
                models["随机森林回归"] = RandomForestRegressor(n_estimators=100, random_state=42)
            if "支持向量回归" in algorithms:
                models["支持向量回归"] = SVR()
            if "决策树回归" in algorithms:
                models["决策树回归"] = DecisionTreeRegressor(random_state=42)
            if "梯度提升回归" in algorithms:
                models["梯度提升回归"] = GradientBoostingRegressor(random_state=42)
            if "岭回归" in algorithms:
                models["岭回归"] = Ridge(random_state=42)
            
            # 训练和评估模型
            results = []
            
            st.write("##### 模型性能比较")
            
            for name, model in models.items():
                # 训练模型
                model.fit(X_train, y_train)
                
                # 预测
                y_pred = model.predict(X_test)
                
                # 计算指标
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)
                cv_scores = cross_val_score(model, X_scaled, y, cv=cv_folds, scoring='r2')
                
                results.append({
                    '算法': name,
                    'R²': f"{r2:.4f}",
                    'RMSE': f"{rmse:.4f}",
                    'MAE': f"{mae:.4f}",
                    '交叉验证R²均值': f"{cv_scores.mean():.4f}",
                    '交叉验证R²标准差': f"{cv_scores.std():.4f}"
                })
            
            results_df = pd.DataFrame(results)
            st.dataframe(results_df)
            
            # 找出最佳模型（基于R²）
            best_model_name = results_df.loc[results_df['R²'].astype(float).idxmax(), '算法']
            st.success(f"🏆 最佳模型: {best_model_name}")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '回归算法比较',
                'target_variable': target_var,
                'feature_variables': feature_vars,
                'algorithms': algorithms,
                'results': results_df.to_dict('records'),
                'best_model': best_model_name
            }
            
            st.success("回归算法比较完成！")
            
        except Exception as e:
            st.error(f"回归算法比较失败: {str(e)}")


def execute_time_series(analysis_option, processor, data):
    """执行时间序列分析"""
    st.write(f"#### 📅 {analysis_option}")
    
    if analysis_option == "趋势分析":
        execute_trend_analysis(data)
    elif analysis_option == "季节性分析":
        execute_seasonal_analysis(data)
    elif analysis_option == "预测分析":
        execute_forecasting_analysis(data)
    elif analysis_option == "异常检测":
        execute_anomaly_detection(data)
    else:
        st.info(f"{analysis_option}功能正在开发中...")


def execute_trend_analysis(data):
    """趋势分析"""
    st.write("##### 趋势分析")
    
    # 检查时间列
    datetime_cols = []
    for col in data.columns:
        if data[col].dtype == 'object':
            try:
                pd.to_datetime(data[col].head())
                datetime_cols.append(col)
            except:
                pass
        elif 'datetime' in str(data[col].dtype):
            datetime_cols.append(col)
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    if not datetime_cols:
        st.error("未找到时间列，请确保数据包含时间信息")
        return
    
    if not numeric_cols:
        st.error("未找到数值列，无法进行趋势分析")
        return
    
    # 选择变量
    col1, col2 = st.columns(2)
    with col1:
        time_col = st.selectbox("选择时间列", datetime_cols)
    with col2:
        value_col = st.selectbox("选择数值列", numeric_cols)
    
    # 趋势分析参数
    col1, col2 = st.columns(2)
    with col1:
        method = st.selectbox("趋势检测方法", ["移动平均", "线性回归", "多项式拟合"])
        if method == "移动平均":
            window = st.slider("移动窗口大小", 3, 30, 7)
        elif method == "多项式拟合":
            degree = st.slider("多项式阶数", 1, 5, 2)
    
    with col2:
        show_decomposition = st.checkbox("显示分解图", value=True)
        detect_changepoints = st.checkbox("检测变点", value=False)
    
    if st.button("执行趋势分析"):
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from scipy import stats
            
            # 准备时间序列数据
            ts_data = data[[time_col, value_col]].dropna().copy()
            ts_data[time_col] = pd.to_datetime(ts_data[time_col])
            ts_data = ts_data.sort_values(time_col).reset_index(drop=True)
            
            if len(ts_data) < 10:
                st.error("时间序列数据点太少，无法进行分析")
                return
            
            # 创建时间索引用于计算
            ts_data['time_index'] = range(len(ts_data))
            
            st.write("##### 时间序列可视化")
            
            # 原始数据图
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            
            # 原始时间序列
            axes[0].plot(ts_data[time_col], ts_data[value_col], 'b-', alpha=0.7, label='原始数据')
            
            # 趋势分析
            if method == "移动平均":
                trend = ts_data[value_col].rolling(window=window, center=True).mean()
                axes[0].plot(ts_data[time_col], trend, 'r-', linewidth=2, label=f'{window}期移动平均')
                
                # 计算趋势方向
                trend_slope = (trend.iloc[-1] - trend.iloc[0]) / len(trend)
                
            elif method == "线性回归":
                slope, intercept, r_value, p_value, std_err = stats.linregress(ts_data['time_index'], ts_data[value_col])
                trend = slope * ts_data['time_index'] + intercept
                axes[0].plot(ts_data[time_col], trend, 'r-', linewidth=2, label='线性趋势')
                
                trend_slope = slope
                
                # 显示回归统计
                st.write("**线性回归统计:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("斜率", f"{slope:.4f}")
                with col2:
                    st.metric("R²", f"{r_value**2:.4f}")
                with col3:
                    st.metric("p值", f"{p_value:.4f}")
                
            elif method == "多项式拟合":
                coeffs = np.polyfit(ts_data['time_index'], ts_data[value_col], degree)
                trend = np.polyval(coeffs, ts_data['time_index'])
                axes[0].plot(ts_data[time_col], trend, 'r-', linewidth=2, label=f'{degree}阶多项式拟合')
                
                # 计算总体趋势方向
                trend_slope = (trend[-1] - trend[0]) / len(trend)
            
            axes[0].set_xlabel('时间')
            axes[0].set_ylabel(value_col)
            axes[0].set_title(f'{value_col} 时间序列趋势分析')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # 残差分析
            if 'trend' in locals():
                residuals = ts_data[value_col] - trend
                axes[1].plot(ts_data[time_col], residuals, 'g-', alpha=0.7, label='残差')
                axes[1].axhline(y=0, color='k', linestyle='--', alpha=0.5)
                axes[1].set_xlabel('时间')
                axes[1].set_ylabel('残差')
                axes[1].set_title('残差分析')
                axes[1].legend()
                axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            
            # 趋势总结
            st.write("##### 趋势分析结果")
            
            if trend_slope > 0:
                trend_direction = "上升"
                trend_icon = "📈"
            elif trend_slope < 0:
                trend_direction = "下降"
                trend_icon = "📉"
            else:
                trend_direction = "平稳"
                trend_icon = "➡️"
            
            st.write(f"{trend_icon} **总体趋势**: {trend_direction}")
            st.write(f"**趋势强度**: {abs(trend_slope):.4f} 单位/期")
            
            # 基本统计
            st.write("##### 基本统计信息")
            stats_df = pd.DataFrame({
                '指标': ['观测数', '均值', '标准差', '最小值', '最大值', '变异系数'],
                '值': [
                    len(ts_data),
                    f"{ts_data[value_col].mean():.4f}",
                    f"{ts_data[value_col].std():.4f}",
                    f"{ts_data[value_col].min():.4f}",
                    f"{ts_data[value_col].max():.4f}",
                    f"{ts_data[value_col].std() / ts_data[value_col].mean():.4f}"
                ]
            })
            st.dataframe(stats_df)
            
            # 变点检测（简化版）
            if detect_changepoints:
                st.write("##### 变点检测")
                try:
                    # 使用简单的统计方法检测变点
                    window_size = min(10, len(ts_data) // 4)
                    if window_size >= 3:
                        changes = []
                        for i in range(window_size, len(ts_data) - window_size):
                            before = ts_data[value_col].iloc[i-window_size:i].mean()
                            after = ts_data[value_col].iloc[i:i+window_size].mean()
                            change_magnitude = abs(after - before)
                            if change_magnitude > ts_data[value_col].std():
                                changes.append({
                                    '时间点': ts_data[time_col].iloc[i],
                                    '变化幅度': change_magnitude,
                                    '变化类型': '上升' if after > before else '下降'
                                })
                        
                        if changes:
                            changes_df = pd.DataFrame(changes)
                            st.dataframe(changes_df)
                            st.info(f"检测到 {len(changes)} 个潜在变点")
                        else:
                            st.info("未检测到明显变点")
                    else:
                        st.info("数据点不足，无法进行变点检测")
                except Exception as e:
                    st.warning(f"变点检测失败: {str(e)}")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '趋势分析',
                'time_column': time_col,
                'value_column': value_col,
                'method': method,
                'trend_direction': trend_direction,
                'trend_slope': trend_slope,
                'data_points': len(ts_data)
            }
            
            st.success("趋势分析完成！")
            
        except Exception as e:
            st.error(f"趋势分析失败: {str(e)}")


def execute_cluster_analysis(data):
    """聚类分析"""
    st.write("#### 🎯 聚类分析")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 2:
        st.error("聚类分析需要至少2个数值型变量")
        return
    
    # 选择用于聚类的变量
    selected_cols = st.multiselect(
        "选择用于聚类的变量", 
        numeric_cols,
        default=numeric_cols[:min(5, len(numeric_cols))],
        help="选择用于聚类的数值型变量"
    )
    
    if len(selected_cols) < 2:
        st.warning("请至少选择2个变量进行聚类分析")
        return
    
    # 聚类参数设置
    col1, col2 = st.columns(2)
    with col1:
        n_clusters = st.slider("聚类数量", 2, 10, 3)
        cluster_method = st.selectbox("聚类方法", ["K-Means", "层次聚类"])
    
    with col2:
        standardize = st.checkbox("标准化数据", value=True, help="建议对数据进行标准化")
        show_details = st.checkbox("显示详细结果", value=True)
    
    if st.button("执行聚类分析"):
        try:
            from sklearn.cluster import KMeans, AgglomerativeClustering
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import silhouette_score
            import numpy as np
            
            # 准备数据
            cluster_data = data[selected_cols].dropna()
            
            if cluster_data.empty:
                st.error("选择的变量中没有有效数据")
                return
            
            # 标准化
            if standardize:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(cluster_data)
                cluster_features = pd.DataFrame(X_scaled, columns=selected_cols, index=cluster_data.index)
            else:
                cluster_features = cluster_data
            
            # 执行聚类
            if cluster_method == "K-Means":
                clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            else:
                clusterer = AgglomerativeClustering(n_clusters=n_clusters)
            
            labels = clusterer.fit_predict(cluster_features)
            
            # 计算聚类评价指标
            silhouette_avg = silhouette_score(cluster_features, labels)
            
            # 显示结果
            st.write("##### 聚类结果")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("聚类数量", n_clusters)
            with col2:
                st.metric("轮廓系数", f"{silhouette_avg:.4f}")
            with col3:
                st.metric("有效样本数", len(cluster_data))
            
            # 聚类分布统计
            cluster_counts = pd.Series(labels).value_counts().sort_index()
            st.write("##### 各聚类样本分布")
            cluster_df = pd.DataFrame({
                '聚类': [f"聚类{i+1}" for i in range(n_clusters)],
                '样本数': [cluster_counts.get(i, 0) for i in range(n_clusters)],
                '占比(%)': [(cluster_counts.get(i, 0) / len(labels) * 100) for i in range(n_clusters)]
            })
            st.dataframe(cluster_df)
            
            if show_details:
                # 各聚类中心
                if cluster_method == "K-Means":
                    centers = clusterer.cluster_centers_
                    if standardize:
                        # 反标准化聚类中心
                        centers = scaler.inverse_transform(centers)
                    
                    centers_df = pd.DataFrame(centers, columns=selected_cols)
                    centers_df.index = [f"聚类{i+1}" for i in range(n_clusters)]
                    
                    st.write("##### 聚类中心")
                    st.dataframe(centers_df.round(3))
                
                # 各聚类的描述统计
                cluster_data_with_labels = cluster_data.copy()
                cluster_data_with_labels['聚类'] = labels
                
                st.write("##### 各聚类描述统计")
                for i in range(n_clusters):
                    with st.expander(f"聚类{i+1} 详细统计"):
                        cluster_i_data = cluster_data_with_labels[cluster_data_with_labels['聚类'] == i][selected_cols]
                        st.dataframe(cluster_i_data.describe().round(3))
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '聚类分析',
                'method': cluster_method,
                'variables': selected_cols,
                'n_clusters': n_clusters,
                'silhouette_score': silhouette_avg,
                'cluster_labels': labels,
                'cluster_centers': centers_df if cluster_method == "K-Means" else None,
                'status': 'completed'
            }
            
            st.success("聚类分析完成！")
            
        except Exception as e:
            st.error(f"聚类分析失败: {str(e)}")


def execute_factor_analysis(data):
    """因子分析"""
    st.write("#### 🔍 因子分析")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 3:
        st.error("因子分析需要至少3个数值型变量")
        return
    
    # 选择用于因子分析的变量
    selected_cols = st.multiselect(
        "选择用于因子分析的变量", 
        numeric_cols,
        default=numeric_cols[:min(10, len(numeric_cols))],
        help="选择用于因子分析的数值型变量，建议选择3-15个变量"
    )
    
    if len(selected_cols) < 3:
        st.warning("请至少选择3个变量进行因子分析")
        return
    
    # 因子分析参数设置
    col1, col2 = st.columns(2)
    with col1:
        n_factors = st.slider("因子数量", 1, min(len(selected_cols)-1, 8), min(3, len(selected_cols)-1))
        rotation = st.selectbox("旋转方法", ["varimax", "quartimax", "none"])
    
    with col2:
        kmo_test = st.checkbox("KMO适合性检验", value=True)
        show_communalities = st.checkbox("显示共同度", value=True)
    
    if st.button("执行因子分析"):
        try:
            from sklearn.decomposition import FactorAnalysis
            from sklearn.preprocessing import StandardScaler
            import numpy as np
            from scipy.stats import chi2
            
            # 准备数据
            factor_data = data[selected_cols].dropna()
            
            if factor_data.empty:
                st.error("选择的变量中没有有效数据")
                return
            
            if len(factor_data) < len(selected_cols) * 2:
                st.warning("样本量可能不足，建议样本量至少是变量数的2倍")
            
            # 标准化数据
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(factor_data)
            factor_features = pd.DataFrame(X_scaled, columns=selected_cols)
            
            # KMO检验
            if kmo_test:
                try:
                    from factor_analyzer.factor_analyzer import calculate_kmo
                    kmo_all, kmo_model = calculate_kmo(factor_features)
                    
                    st.write("##### KMO适合性检验")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("KMO系数", f"{kmo_model:.4f}")
                    with col2:
                        if kmo_model >= 0.8:
                            kmo_level = "优秀"
                            color = "🟢"
                        elif kmo_model >= 0.7:
                            kmo_level = "良好"
                            color = "🔵"
                        elif kmo_model >= 0.6:
                            kmo_level = "可接受"
                            color = "🟡"
                        else:
                            kmo_level = "不适合"
                            color = "🔴"
                        st.write(f"**适合性:** {color} {kmo_level}")
                    
                    if kmo_model < 0.6:
                        st.warning("KMO系数较低，数据可能不适合进行因子分析")
                        
                except ImportError:
                    st.info("未安装factor_analyzer包，跳过KMO检验")
            
            # 执行因子分析
            fa = FactorAnalysis(n_components=n_factors, random_state=42)
            fa.fit(factor_features)
            
            # 因子载荷矩阵
            loadings = fa.components_.T
            loadings_df = pd.DataFrame(
                loadings, 
                columns=[f"因子{i+1}" for i in range(n_factors)],
                index=selected_cols
            )
            
            # 应用旋转（简化版，仅支持varimax）
            if rotation == "varimax":
                try:
                    from scipy.stats import orthogonal_procrustes
                    # 简化的varimax旋转实现
                    from sklearn.decomposition import PCA
                    pca = PCA(n_components=n_factors)
                    pca.fit(factor_features)
                    loadings_df = pd.DataFrame(
                        pca.components_.T,
                        columns=[f"因子{i+1}" for i in range(n_factors)],
                        index=selected_cols
                    )
                except:
                    st.info("旋转计算出现问题，使用未旋转结果")
            
            # 计算共同度
            communalities = np.sum(loadings_df.values**2, axis=1)
            
            # 计算方差贡献
            eigenvalues = np.sum(loadings_df.values**2, axis=0)
            variance_explained = eigenvalues / len(selected_cols) * 100
            cumulative_variance = np.cumsum(variance_explained)
            
            # 显示结果
            st.write("##### 因子分析结果")
            
            # 方差解释表
            variance_df = pd.DataFrame({
                '因子': [f"因子{i+1}" for i in range(n_factors)],
                '特征值': eigenvalues,
                '方差贡献率(%)': variance_explained,
                '累积贡献率(%)': cumulative_variance
            })
            
            st.write("**方差解释:**")
            st.dataframe(variance_df.round(3))
            
            # 因子载荷矩阵
            st.write("**因子载荷矩阵:**")
            # 突出显示高载荷（绝对值>0.5）
            def highlight_loadings(val):
                if abs(val) >= 0.5:
                    return 'background-color: lightgreen'
                elif abs(val) >= 0.3:
                    return 'background-color: lightyellow'
                return ''
            
            styled_loadings = loadings_df.round(3).style.map(highlight_loadings)
            st.dataframe(styled_loadings)
            
            # 共同度
            if show_communalities:
                communalities_df = pd.DataFrame({
                    '变量': selected_cols,
                    '共同度': communalities
                })
                communalities_df = communalities_df.sort_values('共同度', ascending=False)
                
                st.write("**共同度:**")
                st.dataframe(communalities_df.round(3))
                
                # 共同度解释
                low_communality = communalities_df[communalities_df['共同度'] < 0.4]
                if not low_communality.empty:
                    st.warning(f"以下变量的共同度较低(<0.4)，可能需要考虑移除: {', '.join(low_communality['变量'].tolist())}")
            
            # 因子命名建议
            st.write("##### 因子解释建议")
            for i in range(n_factors):
                factor_name = f"因子{i+1}"
                high_loadings = loadings_df[abs(loadings_df[factor_name]) >= 0.5]
                if not high_loadings.empty:
                    st.write(f"**{factor_name}** (贡献率: {variance_explained[i]:.1f}%)")
                    st.write("主要变量:", ", ".join(high_loadings.index.tolist()))
                else:
                    st.write(f"**{factor_name}**: 无明显高载荷变量")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '因子分析',
                'variables': selected_cols,
                'n_factors': n_factors,
                'loadings_matrix': loadings_df,
                'communalities': communalities_df if show_communalities else None,
                'variance_explained': variance_df,
                'rotation': rotation,
                'kmo_score': kmo_model if kmo_test else None,
                'status': 'completed'
            }
            
            st.success("因子分析完成！")
            
        except Exception as e:
            st.error(f"因子分析失败: {str(e)}")
            st.write("请确保安装了所需的统计包，或尝试减少因子数量")


def execute_pca_analysis(data):
    """主成分分析"""
    st.write("#### 🎯 主成分分析 (PCA)")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 2:
        st.error("主成分分析需要至少2个数值型变量")
        return
    
    # 选择用于PCA的变量
    selected_cols = st.multiselect(
        "选择用于主成分分析的变量", 
        numeric_cols,
        default=numeric_cols[:min(10, len(numeric_cols))],
        help="选择用于主成分分析的数值型变量"
    )
    
    if len(selected_cols) < 2:
        st.warning("请至少选择2个变量进行主成分分析")
        return
    
    # PCA参数设置
    col1, col2 = st.columns(2)
    with col1:
        n_components = st.slider("主成分数量", 1, len(selected_cols), min(3, len(selected_cols)))
        standardize = st.checkbox("标准化数据", value=True, help="建议对不同量纲的数据进行标准化")
    
    with col2:
        show_biplot = st.checkbox("显示双标图", value=True)
        show_loadings = st.checkbox("显示载荷矩阵", value=True)
    
    if st.button("执行主成分分析"):
        try:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import StandardScaler
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 准备数据
            pca_data = data[selected_cols].dropna()
            
            if pca_data.empty:
                st.error("选择的变量中没有有效数据")
                return
            
            # 标准化数据（如果选择）
            if standardize:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(pca_data)
                X_for_pca = pd.DataFrame(X_scaled, columns=selected_cols, index=pca_data.index)
            else:
                X_for_pca = pca_data
            
            # 执行PCA
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(X_for_pca)
            
            # 创建主成分DataFrame
            pc_columns = [f'PC{i+1}' for i in range(n_components)]
            pca_df = pd.DataFrame(pca_result, columns=pc_columns, index=pca_data.index)
            
            # 显示结果
            st.write("##### 主成分分析结果")
            
            # 方差解释表
            variance_ratio = pca.explained_variance_ratio_ * 100
            cumulative_variance = np.cumsum(variance_ratio)
            
            variance_df = pd.DataFrame({
                '主成分': pc_columns,
                '特征值': pca.explained_variance_,
                '方差贡献率(%)': variance_ratio,
                '累积贡献率(%)': cumulative_variance
            })
            
            st.write("**方差解释:**")
            st.dataframe(variance_df.round(3))
            
            # 可视化方差贡献
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 碎石图
            ax1.plot(range(1, n_components + 1), pca.explained_variance_, 'bo-')
            ax1.set_xlabel('主成分')
            ax1.set_ylabel('特征值')
            ax1.set_title('碎石图')
            ax1.grid(True, alpha=0.3)
            
            # 方差贡献率图
            ax2.bar(range(1, n_components + 1), variance_ratio, alpha=0.7, label='单独贡献')
            ax2.plot(range(1, n_components + 1), cumulative_variance, 'ro-', label='累积贡献')
            ax2.set_xlabel('主成分')
            ax2.set_ylabel('方差贡献率 (%)')
            ax2.set_title('方差贡献率')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            
            # 载荷矩阵
            if show_loadings:
                st.write("**主成分载荷矩阵:**")
                loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
                loadings_df = pd.DataFrame(
                    loadings,
                    columns=pc_columns,
                    index=selected_cols
                )
                
                # 突出显示高载荷
                def highlight_loadings(val):
                    if abs(val) >= 0.7:
                        return 'background-color: lightgreen'
                    elif abs(val) >= 0.5:
                        return 'background-color: lightyellow'
                    return ''
                
                styled_loadings = loadings_df.round(3).style.map(highlight_loadings)
                st.dataframe(styled_loadings)
                
                # 载荷解释
                st.write("**主成分解释:**")
                for i, pc in enumerate(pc_columns):
                    high_positive = loadings_df[loadings_df[pc] >= 0.5].index.tolist()
                    high_negative = loadings_df[loadings_df[pc] <= -0.5].index.tolist()
                    
                    st.write(f"**{pc}** (贡献率: {variance_ratio[i]:.1f}%)")
                    if high_positive:
                        st.write(f"  正向高载荷: {', '.join(high_positive)}")
                    if high_negative:
                        st.write(f"  负向高载荷: {', '.join(high_negative)}")
                    if not high_positive and not high_negative:
                        st.write("  无明显高载荷变量")
            
            # 双标图
            if show_biplot and n_components >= 2:
                st.write("##### 双标图 (前两个主成分)")
                
                fig, ax = plt.subplots(figsize=(10, 8))
                
                # 绘制观测点
                scatter = ax.scatter(pca_result[:, 0], pca_result[:, 1], alpha=0.6, s=50)
                
                # 绘制变量向量
                if show_loadings:
                    for i, var in enumerate(selected_cols):
                        ax.arrow(0, 0, loadings_df.iloc[i, 0]*3, loadings_df.iloc[i, 1]*3,
                                head_width=0.1, head_length=0.1, fc='red', ec='red', alpha=0.8)
                        ax.text(loadings_df.iloc[i, 0]*3.2, loadings_df.iloc[i, 1]*3.2, var,
                               fontsize=10, ha='center', va='center')
                
                ax.set_xlabel(f'PC1 ({variance_ratio[0]:.1f}%)')
                ax.set_ylabel(f'PC2 ({variance_ratio[1]:.1f}%)')
                ax.set_title('PCA双标图')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
                ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            
            # 主成分得分
            st.write("##### 主成分得分 (前10行)")
            st.dataframe(pca_df.head(10).round(4))
            
            # 数据质量评估
            st.write("##### 数据质量评估")
            
            # 计算Kaiser准则（特征值>1）
            kaiser_components = np.sum(pca.explained_variance_ > 1)
            st.write(f"**Kaiser准则**: {kaiser_components} 个主成分的特征值大于1")
            
            # 计算累积方差达到80%的主成分数
            variance_80_components = np.argmax(cumulative_variance >= 80) + 1
            st.write(f"**80%方差准则**: 前 {variance_80_components} 个主成分可解释80%的方差")
            
            # 相关矩阵
            if len(selected_cols) <= 10:
                st.write("##### 原始变量相关矩阵")
                corr_matrix = pca_data.corr()
                
                # 相关矩阵热力图
                fig, ax = plt.subplots(figsize=(10, 8))
                import seaborn as sns
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                           square=True, linewidths=.5, ax=ax)
                ax.set_title('原始变量相关矩阵')
                st.pyplot(fig)
                plt.close(fig)
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '主成分分析',
                'variables': selected_cols,
                'n_components': n_components,
                'variance_explained': variance_df.to_dict('records'),
                'loadings_matrix': loadings_df.to_dict() if show_loadings else None,
                'pca_scores': pca_df.to_dict('records'),
                'kaiser_components': kaiser_components,
                'variance_80_components': variance_80_components,
                'standardized': standardize
            }
            
            st.success("主成分分析完成！")
            
        except Exception as e:
            st.error(f"主成分分析失败: {str(e)}")


def execute_clustering_algorithms(data):
    """聚类算法比较"""
    st.write("##### 聚类算法比较")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.error("聚类分析需要至少2个数值型变量")
        return
    
    # 选择变量
    feature_vars = st.multiselect("选择聚类变量", 
                                numeric_cols,
                                default=numeric_cols[:min(5, len(numeric_cols))])
    
    if len(feature_vars) < 2:
        st.warning("请选择至少2个变量进行聚类")
        return
    
    # 算法选择
    algorithms = st.multiselect(
        "选择聚类算法",
        ["K-Means", "层次聚类", "DBSCAN", "Gaussian混合模型"],
        default=["K-Means", "层次聚类"]
    )
    
    if not algorithms:
        st.warning("请选择至少一个算法")
        return
    
    # 参数设置
    col1, col2 = st.columns(2)
    with col1:
        n_clusters = st.slider("聚类数量", 2, 10, 3)
        standardize = st.checkbox("标准化数据", value=True)
    
    with col2:
        show_plots = st.checkbox("显示聚类图", value=True)
        evaluate_metrics = st.checkbox("评估指标", value=True)
    
    if st.button("执行聚类算法比较"):
        try:
            from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
            from sklearn.mixture import GaussianMixture
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 准备数据
            cluster_data = data[feature_vars].dropna()
            
            if len(cluster_data) < 10:
                st.error("样本量太少，无法进行聚类分析")
                return
            
            # 标准化数据
            if standardize:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(cluster_data)
                X_for_cluster = pd.DataFrame(X_scaled, columns=feature_vars, index=cluster_data.index)
            else:
                X_for_cluster = cluster_data
            
            # 定义算法
            models = {}
            if "K-Means" in algorithms:
                models["K-Means"] = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            if "层次聚类" in algorithms:
                models["层次聚类"] = AgglomerativeClustering(n_clusters=n_clusters)
            if "DBSCAN" in algorithms:
                eps = st.slider("DBSCAN eps参数", 0.1, 2.0, 0.5, 0.1, key="dbscan_eps")
                min_samples = st.slider("DBSCAN min_samples参数", 2, 20, 5, key="dbscan_min_samples")
                models["DBSCAN"] = DBSCAN(eps=eps, min_samples=min_samples)
            if "Gaussian混合模型" in algorithms:
                models["Gaussian混合模型"] = GaussianMixture(n_components=n_clusters, random_state=42)
            
            # 执行聚类并评估
            results = []
            cluster_results = {}
            
            st.write("##### 聚类结果比较")
            
            for name, model in models.items():
                try:
                    # 聚类
                    if name == "Gaussian混合模型":
                        labels = model.fit_predict(X_for_cluster)
                    else:
                        labels = model.fit_predict(X_for_cluster)
                    
                    cluster_results[name] = labels
                    
                    # 评估指标
                    if evaluate_metrics and len(np.unique(labels)) > 1:
                        if len(np.unique(labels[labels != -1])) > 1:  # 排除噪声点
                            valid_mask = labels != -1  # 排除DBSCAN的噪声点
                            if np.sum(valid_mask) > 1:
                                silhouette = silhouette_score(X_for_cluster[valid_mask], labels[valid_mask])
                                calinski = calinski_harabasz_score(X_for_cluster[valid_mask], labels[valid_mask])
                                davies_bouldin = davies_bouldin_score(X_for_cluster[valid_mask], labels[valid_mask])
                            else:
                                silhouette = calinski = davies_bouldin = np.nan
                        else:
                            silhouette = calinski = davies_bouldin = np.nan
                    else:
                        silhouette = calinski = davies_bouldin = np.nan
                    
                    # 统计聚类数量
                    unique_labels = np.unique(labels)
                    n_clusters_found = len(unique_labels)
                    n_noise = np.sum(labels == -1) if -1 in unique_labels else 0
                    
                    results.append({
                        '算法': name,
                        '聚类数量': n_clusters_found - (1 if -1 in unique_labels else 0),
                        '噪声点数': n_noise,
                        '轮廓系数': f"{silhouette:.4f}" if not np.isnan(silhouette) else "N/A",
                        'Calinski-Harabasz': f"{calinski:.4f}" if not np.isnan(calinski) else "N/A",
                        'Davies-Bouldin': f"{davies_bouldin:.4f}" if not np.isnan(davies_bouldin) else "N/A"
                    })
                    
                except Exception as e:
                    st.warning(f"{name} 聚类失败: {str(e)}")
                    continue
            
            if results:
                results_df = pd.DataFrame(results)
                st.dataframe(results_df)
                
                # 可视化聚类结果
                if show_plots and len(feature_vars) >= 2:
                    st.write("##### 聚类可视化 (前两个变量)")
                    
                    n_algorithms = len(cluster_results)
                    if n_algorithms > 0:
                        cols_per_row = min(2, n_algorithms)
                        n_rows = (n_algorithms + cols_per_row - 1) // cols_per_row
                        
                        fig, axes = plt.subplots(n_rows, cols_per_row, figsize=(15, 5*n_rows))
                        if n_rows == 1 and cols_per_row == 1:
                            axes = [axes]
                        elif n_rows == 1:
                            axes = [axes]
                        else:
                            axes = axes.flatten()
                        
                        for idx, (name, labels) in enumerate(cluster_results.items()):
                            ax = axes[idx] if n_algorithms > 1 else axes[0]
                            
                            # 使用前两个变量绘图
                            x_col, y_col = feature_vars[0], feature_vars[1]
                            
                            # 为每个聚类分配颜色
                            unique_labels = np.unique(labels)
                            colors = plt.cm.Set1(np.linspace(0, 1, len(unique_labels)))
                            
                            for label, color in zip(unique_labels, colors):
                                if label == -1:  # 噪声点
                                    mask = labels == label
                                    ax.scatter(cluster_data.iloc[mask][x_col], 
                                             cluster_data.iloc[mask][y_col], 
                                             c='black', marker='x', s=50, alpha=0.6, label='噪声')
                                else:
                                    mask = labels == label
                                    ax.scatter(cluster_data.iloc[mask][x_col], 
                                             cluster_data.iloc[mask][y_col], 
                                             c=[color], s=50, alpha=0.7, label=f'簇{label}')
                            
                            ax.set_xlabel(x_col)
                            ax.set_ylabel(y_col)
                            ax.set_title(f'{name} 聚类结果')
                            ax.legend()
                            ax.grid(True, alpha=0.3)
                        
                        # 隐藏多余的子图
                        for idx in range(len(cluster_results), len(axes)):
                            axes[idx].set_visible(False)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close(fig)
                
                # 聚类解释
                st.write("##### 聚类解释")
                st.write("**评估指标说明:**")
                st.write("- **轮廓系数**: 范围[-1,1]，越接近1越好")
                st.write("- **Calinski-Harabasz指数**: 越大越好")
                st.write("- **Davies-Bouldin指数**: 越小越好")
                
                # 推荐最佳算法
                if evaluate_metrics:
                    valid_results = [r for r in results if r['轮廓系数'] != "N/A"]
                    if valid_results:
                        best_silhouette = max(valid_results, key=lambda x: float(x['轮廓系数']))
                        st.success(f"🏆 基于轮廓系数的推荐算法: {best_silhouette['算法']}")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '聚类算法比较',
                'feature_variables': feature_vars,
                'algorithms': algorithms,
                'n_clusters': n_clusters,
                'results': results_df.to_dict('records') if results else [],
                'cluster_labels': {name: labels.tolist() for name, labels in cluster_results.items()},
                'standardized': standardize
            }
            
            st.success("聚类算法比较完成！")
            
        except Exception as e:
            st.error(f"聚类算法比较失败: {str(e)}")


def execute_dimensionality_reduction(data):
    """降维算法"""
    st.write("##### 降维算法比较")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 3:
        st.error("降维分析需要至少3个数值型变量")
        return
    
    # 选择变量
    feature_vars = st.multiselect("选择特征变量", 
                                numeric_cols,
                                default=numeric_cols[:min(10, len(numeric_cols))])
    
    if len(feature_vars) < 3:
        st.warning("请选择至少3个变量进行降维")
        return
    
    # 算法选择
    algorithms = st.multiselect(
        "选择降维算法",
        ["PCA", "t-SNE", "UMAP", "因子分析"],
        default=["PCA", "t-SNE"]
    )
    
    if not algorithms:
        st.warning("请选择至少一个算法")
        return
    
    # 参数设置
    col1, col2 = st.columns(2)
    with col1:
        n_components = st.slider("降维后维数", 2, min(5, len(feature_vars)-1), 2)
        standardize = st.checkbox("标准化数据", value=True)
    
    with col2:
        show_plots = st.checkbox("显示降维图", value=True)
        show_variance = st.checkbox("显示方差解释", value=True)
    
    if st.button("执行降维算法比较"):
        try:
            from sklearn.decomposition import PCA, FactorAnalysis
            from sklearn.manifold import TSNE
            from sklearn.preprocessing import StandardScaler
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 准备数据
            dim_data = data[feature_vars].dropna()
            
            if len(dim_data) < 10:
                st.error("样本量太少，无法进行降维分析")
                return
            
            # 标准化数据
            if standardize:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(dim_data)
                X_for_dim = pd.DataFrame(X_scaled, columns=feature_vars, index=dim_data.index)
            else:
                X_for_dim = dim_data
            
            # 执行降维算法
            results = {}
            variance_info = {}
            
            st.write("##### 降维结果比较")
            
            for algorithm in algorithms:
                try:
                    if algorithm == "PCA":
                        model = PCA(n_components=n_components, random_state=42)
                        transformed = model.fit_transform(X_for_dim)
                        variance_info[algorithm] = {
                            'explained_variance_ratio': model.explained_variance_ratio_,
                            'cumulative_variance': np.cumsum(model.explained_variance_ratio_)
                        }
                        
                    elif algorithm == "t-SNE":
                        perplexity = min(30, len(X_for_dim) - 1)
                        model = TSNE(n_components=n_components, random_state=42, perplexity=perplexity)
                        transformed = model.fit_transform(X_for_dim)
                        
                    elif algorithm == "因子分析":
                        model = FactorAnalysis(n_components=n_components, random_state=42)
                        transformed = model.fit_transform(X_for_dim)
                        
                    elif algorithm == "UMAP":
                        try:
                            import umap
                            model = umap.UMAP(n_components=n_components, random_state=42)
                            transformed = model.fit_transform(X_for_dim)
                        except ImportError:
                            st.warning("UMAP需要安装umap-learn包，跳过此算法")
                            continue
                    
                    # 存储结果
                    results[algorithm] = transformed
                    
                    st.write(f"**{algorithm}**: 成功降维到 {n_components} 维")
                    
                except Exception as e:
                    st.warning(f"{algorithm} 降维失败: {str(e)}")
                    continue
            
            # 显示方差解释（对于支持的算法）
            if show_variance and variance_info:
                st.write("##### 方差解释")
                for alg, info in variance_info.items():
                    st.write(f"**{alg}**:")
                    for i, (var_ratio, cum_var) in enumerate(zip(info['explained_variance_ratio'], 
                                                               info['cumulative_variance'])):
                        st.write(f"  PC{i+1}: {var_ratio:.3f} ({cum_var:.3f} 累积)")
            
            # 可视化降维结果
            if show_plots and results and n_components >= 2:
                st.write("##### 降维可视化")
                
                n_algorithms = len(results)
                if n_algorithms > 0:
                    cols_per_row = min(2, n_algorithms)
                    n_rows = (n_algorithms + cols_per_row - 1) // cols_per_row
                    
                    fig, axes = plt.subplots(n_rows, cols_per_row, figsize=(15, 5*n_rows))
                    if n_rows == 1 and cols_per_row == 1:
                        axes = [axes]
                    elif n_rows == 1:
                        axes = [axes]
                    else:
                        axes = axes.flatten()
                    
                    for idx, (name, transformed_data) in enumerate(results.items()):
                        ax = axes[idx] if n_algorithms > 1 else axes[0]
                        
                        # 绘制前两个维度
                        scatter = ax.scatter(transformed_data[:, 0], transformed_data[:, 1], 
                                           alpha=0.6, s=50, c=range(len(transformed_data)), cmap='viridis')
                        
                        ax.set_xlabel('维度 1')
                        ax.set_ylabel('维度 2')
                        ax.set_title(f'{name} 降维结果')
                        ax.grid(True, alpha=0.3)
                        
                        # 添加颜色条
                        plt.colorbar(scatter, ax=ax, label='样本索引')
                    
                    # 隐藏多余的子图
                    for idx in range(len(results), len(axes)):
                        axes[idx].set_visible(False)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)
            
            # 算法比较建议
            st.write("##### 算法选择建议")
            st.write("**算法特点:**")
            st.write("- **PCA**: 线性降维，保持方差最大化，适合线性关系")
            st.write("- **t-SNE**: 非线性降维，保持局部结构，适合可视化")
            st.write("- **UMAP**: 非线性降维，保持全局和局部结构，速度较快")
            st.write("- **因子分析**: 假设潜在因子模型，适合心理学和社会科学")
            
            if variance_info and "PCA" in variance_info:
                pca_var = variance_info["PCA"]["cumulative_variance"][-1]
                if pca_var >= 0.8:
                    st.success(f"✅ PCA能解释 {pca_var:.1%} 的方差，线性降维效果良好")
                else:
                    st.info(f"ℹ️ PCA只能解释 {pca_var:.1%} 的方差，可能需要非线性方法")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '降维算法比较',
                'feature_variables': feature_vars,
                'algorithms': list(results.keys()),
                'n_components': n_components,
                'variance_info': variance_info,
                'transformed_shapes': {name: data.shape for name, data in results.items()},
                'standardized': standardize
            }
            
            st.success("降维算法比较完成！")
            
        except Exception as e:
            st.error(f"降维算法比较失败: {str(e)}")


def execute_model_evaluation(data):
    """模型评估"""
    st.write("##### 模型评估工具")
    st.info("模型评估功能将帮助您评估已训练模型的性能")
    
    # 这里可以添加模型评估的具体功能
    # 例如交叉验证、学习曲线、ROC曲线等
    st.write("功能开发中...")
    st.write("#### 📊 主成分分析")
    st.info("主成分分析功能正在开发中...")


def execute_anova_analysis(data):
    """方差分析"""
    st.write("#### 📈 方差分析")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not numeric_cols:
        st.error("方差分析需要至少一个数值型因变量")
        return
    
    if not categorical_cols:
        st.error("方差分析需要至少一个分类型自变量")
        return
    
    # 选择变量
    st.write("##### 变量选择")
    dependent_var = st.selectbox("选择因变量（数值型）", numeric_cols)
    independent_vars = st.multiselect(
        "选择自变量（分类型）", 
        categorical_cols,
        help="可以选择多个分类变量进行多因素方差分析"
    )
    
    if not independent_vars:
        st.warning("请至少选择一个分类型自变量")
        return
    
    # 分析类型选择
    if len(independent_vars) == 1:
        analysis_type = "单因素方差分析"
    else:
        analysis_type = st.selectbox(
            "分析类型",
            ["多因素方差分析", "单因素方差分析（逐个检验）"]
        )
    
    # 其他选项
    col1, col2 = st.columns(2)
    with col1:
        alpha_level = st.selectbox("显著性水平", [0.05, 0.01, 0.001], index=0)
        post_hoc = st.checkbox("事后比较检验", value=True)
    
    with col2:
        descriptive_stats = st.checkbox("描述统计", value=True)
        homogeneity_test = st.checkbox("方差齐性检验", value=True)
    
    if st.button("执行方差分析"):
        try:
            from scipy import stats
            import numpy as np
            
            # 准备数据
            analysis_data = data[[dependent_var] + independent_vars].dropna()
            
            if analysis_data.empty:
                st.error("没有有效的数据进行分析")
                return
            
            if len(analysis_data) < 3:
                st.error("样本量太小，无法进行方差分析")
                return
            
            st.write("##### 方差分析结果")
            
            # 描述统计
            if descriptive_stats:
                st.write("**描述统计:**")
                if len(independent_vars) == 1:
                    desc_stats = analysis_data.groupby(independent_vars[0])[dependent_var].agg([
                        'count', 'mean', 'std', 'min', 'max'
                    ]).round(3)
                    desc_stats.columns = ['样本量', '均值', '标准差', '最小值', '最大值']
                    st.dataframe(desc_stats)
                else:
                    # 多因素描述统计
                    for var in independent_vars:
                        st.write(f"按 {var} 分组:")
                        desc_stats = analysis_data.groupby(var)[dependent_var].agg([
                            'count', 'mean', 'std'
                        ]).round(3)
                        desc_stats.columns = ['样本量', '均值', '标准差']
                        st.dataframe(desc_stats)
            
            # 执行方差分析
            if len(independent_vars) == 1 or analysis_type == "单因素方差分析（逐个检验）":
                # 单因素方差分析
                for var in independent_vars:
                    st.write(f"**{var} 的单因素方差分析:**")
                    
                    groups = []
                    group_names = []
                    for group_name in analysis_data[var].unique():
                        group_data = analysis_data[analysis_data[var] == group_name][dependent_var]
                        if len(group_data) > 0:
                            groups.append(group_data)
                            group_names.append(str(group_name))
                    
                    if len(groups) < 2:
                        st.warning(f"变量 {var} 的有效组别少于2个，无法进行方差分析")
                        continue
                    
                    # 方差齐性检验（Levene检验）
                    if homogeneity_test and len(groups) >= 2:
                        try:
                            levene_stat, levene_p = stats.levene(*groups)
                            st.write(f"**Levene方差齐性检验:**")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Levene统计量", f"{levene_stat:.4f}")
                            with col2:
                                st.metric("p值", f"{levene_p:.4f}")
                            
                            if levene_p < alpha_level:
                                st.warning("⚠️ 方差不齐，违反了方差分析的假设")
                            else:
                                st.success("✅ 方差齐性假设满足")
                        except:
                            st.info("无法进行方差齐性检验")
                    
                    # 执行单因素方差分析
                    try:
                        f_stat, p_value = stats.f_oneway(*groups)
                        
                        # 计算效应量（eta squared）
                        ss_between = sum(len(group) * (np.mean(group) - np.mean(analysis_data[dependent_var]))**2 for group in groups)
                        ss_total = np.sum((analysis_data[dependent_var] - np.mean(analysis_data[dependent_var]))**2)
                        eta_squared = ss_between / ss_total if ss_total > 0 else 0
                        
                        # 显示结果
                        st.write("**ANOVA结果:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("F统计量", f"{f_stat:.4f}")
                        with col2:
                            st.metric("p值", f"{p_value:.4f}")
                        with col3:
                            st.metric("η²", f"{eta_squared:.4f}")
                        
                        # 显著性判断
                        if p_value < alpha_level:
                            st.success(f"✅ 结果显著 (p < {alpha_level})，组间存在显著差异")
                            
                            # 事后比较
                            if post_hoc and len(groups) > 2:
                                st.write("**事后比较 (Tukey HSD):**")
                                try:
                                    from scipy.stats import tukey_hsd
                                    tukey_result = tukey_hsd(*groups)
                                    
                                    # 创建事后比较表
                                    comparisons = []
                                    for i in range(len(group_names)):
                                        for j in range(i+1, len(group_names)):
                                            p_adj = tukey_result.pvalue[i, j]
                                            mean_diff = np.mean(groups[i]) - np.mean(groups[j])
                                            comparisons.append({
                                                '比较': f"{group_names[i]} vs {group_names[j]}",
                                                '均值差': f"{mean_diff:.3f}",
                                                '调整p值': f"{p_adj:.4f}",
                                                '显著性': "是" if p_adj < alpha_level else "否"
                                            })
                                    
                                    comparison_df = pd.DataFrame(comparisons)
                                    st.dataframe(comparison_df)
                                    
                                except ImportError:
                                    st.info("事后比较需要更新的scipy版本，使用简单的成对t检验")
                                    # 简单的成对比较
                                    comparisons = []
                                    for i in range(len(group_names)):
                                        for j in range(i+1, len(group_names)):
                                            t_stat, p_val = stats.ttest_ind(groups[i], groups[j])
                                            mean_diff = np.mean(groups[i]) - np.mean(groups[j])
                                            comparisons.append({
                                                '比较': f"{group_names[i]} vs {group_names[j]}",
                                                '均值差': f"{mean_diff:.3f}",
                                                't统计量': f"{t_stat:.3f}",
                                                'p值': f"{p_val:.4f}",
                                                '显著性': "是" if p_val < alpha_level else "否"
                                            })
                                    
                                    comparison_df = pd.DataFrame(comparisons)
                                    st.dataframe(comparison_df)
                        else:
                            st.info(f"结果不显著 (p ≥ {alpha_level})，组间无显著差异")
                        
                    except Exception as e:
                        st.error(f"方差分析计算失败: {str(e)}")
            
            else:
                # 多因素方差分析（简化版）
                st.info("多因素方差分析功能需要更高级的统计库支持，当前使用简化分析")
                for var in independent_vars:
                    st.write(f"**{var} 的独立效应:**")
                    groups = [analysis_data[analysis_data[var] == group][dependent_var] 
                             for group in analysis_data[var].unique()]
                    groups = [g for g in groups if len(g) > 0]
                    
                    if len(groups) >= 2:
                        f_stat, p_value = stats.f_oneway(*groups)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("F统计量", f"{f_stat:.4f}")
                        with col2:
                            st.metric("p值", f"{p_value:.4f}")
                        
                        if p_value < alpha_level:
                            st.success("✅ 显著")
                        else:
                            st.info("不显著")
            
            # 存储结果
            st.session_state.analysis_results = {
                'type': '方差分析',
                'dependent_var': dependent_var,
                'independent_vars': independent_vars,
                'analysis_type': analysis_type,
                'alpha_level': alpha_level,
                'status': 'completed'
            }
            
            st.success("方差分析完成！")
            
        except Exception as e:
            st.error(f"方差分析失败: {str(e)}")
            st.write("错误详情:", str(e))


def execute_single_analysis(module, analysis_option, processor, data):
    """执行单个分析方法并返回结果"""
    try:
        # 根据模块执行对应的分析
        if module == "数据处理":
            return execute_data_processing_single(analysis_option, processor, data)
        elif module == "通用方法":
            return execute_general_methods_single(analysis_option, processor, data)
        elif module == "问卷研究":
            return execute_questionnaire_analysis_single(analysis_option, processor, data)
        elif module == "进阶方法":
            return execute_advanced_methods_single(analysis_option, processor, data)
        elif module == "机器学习":
            return execute_machine_learning_single(analysis_option, processor, data)
        elif module == "时间序列":
            return execute_time_series_single(analysis_option, processor, data)
        else:
            return None
    except Exception as e:
        st.error(f"执行 {analysis_option} 时出错: {str(e)}")
        return {"error": str(e)}


def execute_data_processing_single(analysis_option, processor, data):
    """执行单个数据处理分析"""
    if analysis_option == "数据清洗":
        # 执行数据清洗并返回结果
        missing_count = data.isnull().sum().sum()
        duplicate_count = data.duplicated().sum()
        return {
            'type': '数据清洗',
            'original_shape': data.shape,
            'missing_count': missing_count,
            'duplicate_count': duplicate_count,
            'status': 'completed'
        }
    return {"status": "not_implemented", "message": f"{analysis_option}功能正在开发中"}


def execute_general_methods_single(analysis_option, processor, data):
    """执行单个通用方法分析"""
    if analysis_option == "频数分析":
        # 自动选择第一个合适的列进行频数分析
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        
        if categorical_cols:
            col = categorical_cols[0]
            freq_table = data[col].value_counts().reset_index()
            freq_table.columns = ['类别', '频数']
            freq_table['百分比'] = (freq_table['频数'] / freq_table['频数'].sum() * 100).round(2)
        elif numeric_cols:
            col = numeric_cols[0]
            freq_table = pd.cut(data[col], bins=10).value_counts().reset_index()
            freq_table.columns = ['区间', '频数']
            freq_table['百分比'] = (freq_table['频数'] / freq_table['频数'].sum() * 100).round(2)
        else:
            return {"error": "没有合适的列进行频数分析"}
            
        return {
            'type': '频数分析',
            'variable': col,
            'frequency_table': freq_table,
            'status': 'completed'
        }
    
    elif analysis_option == "描述统计":
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return {"error": "没有数值型变量进行描述统计"}
        
        desc_stats = data[numeric_cols[:5]].describe().round(3)
        return {
            'type': '描述统计',
            'variables': numeric_cols[:5],
            'descriptive_stats': desc_stats,
            'status': 'completed'
        }
    
    return {"status": "not_implemented", "message": f"{analysis_option}功能正在开发中"}


def execute_questionnaire_analysis_single(analysis_option, processor, data):
    """执行单个问卷研究分析"""
    if analysis_option == "信度分析":
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 2:
            return {"error": "信度分析需要至少2个数值型变量"}
        
        try:
            reliability_results = processor.reliability_analysis(data[numeric_cols[:min(10, len(numeric_cols))]])
            return {
                'type': '信度分析',
                'variables': numeric_cols[:min(10, len(numeric_cols))],
                'reliability_results': reliability_results,
                'status': 'completed'
            }
        except Exception as e:
            return {"error": f"信度分析失败: {str(e)}"}
    
    return {"status": "not_implemented", "message": f"{analysis_option}功能正在开发中"}


def execute_advanced_methods_single(analysis_option, processor, data):
    """执行单个进阶方法分析"""
    if analysis_option == "线性回归":
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 2:
            return {"error": "线性回归需要至少2个数值型变量"}
        
        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import r2_score, mean_squared_error
            import numpy as np
            
            # 自动选择前两个数值列
            y_var = numeric_cols[0]
            x_vars = numeric_cols[1:min(4, len(numeric_cols))]
            
            X = data[x_vars].dropna()
            y = data[y_var].dropna()
            
            common_index = X.index.intersection(y.index)
            X = X.loc[common_index]
            y = y.loc[common_index]
            
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            return {
                'type': '线性回归',
                'dependent_var': y_var,
                'independent_vars': x_vars,
                'r2_score': r2,
                'rmse': rmse,
                'status': 'completed'
            }
        except Exception as e:
            return {"error": f"线性回归分析失败: {str(e)}"}
    
    elif analysis_option == "聚类分析":
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 2:
            return {"error": "聚类分析需要至少2个数值型变量"}
        
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import silhouette_score
            
            # 自动选择前5个数值列
            selected_cols = numeric_cols[:min(5, len(numeric_cols))]
            cluster_data = data[selected_cols].dropna()
            
            if len(cluster_data) < 4:
                return {"error": "样本量太小，无法进行聚类分析"}
            
            # 标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(cluster_data)
            
            # K-means聚类
            n_clusters = 3  # 默认3个聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            
            # 计算轮廓系数
            silhouette_avg = silhouette_score(X_scaled, labels)
            
            return {
                'type': '聚类分析',
                'variables': selected_cols,
                'n_clusters': n_clusters,
                'silhouette_score': silhouette_avg,
                'n_samples': len(cluster_data),
                'status': 'completed'
            }
        except Exception as e:
            return {"error": f"聚类分析失败: {str(e)}"}
    
    elif analysis_option == "因子分析":
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 3:
            return {"error": "因子分析需要至少3个数值型变量"}
        
        try:
            from sklearn.decomposition import FactorAnalysis
            from sklearn.preprocessing import StandardScaler
            import numpy as np
            
            # 自动选择前8个数值列
            selected_cols = numeric_cols[:min(8, len(numeric_cols))]
            factor_data = data[selected_cols].dropna()
            
            if len(factor_data) < len(selected_cols) * 2:
                return {"error": "样本量不足，建议样本量至少是变量数的2倍"}
            
            # 标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(factor_data)
            
            # 因子分析
            n_factors = min(3, len(selected_cols) - 1)
            fa = FactorAnalysis(n_components=n_factors, random_state=42)
            fa.fit(X_scaled)
            
            # 计算方差解释比例
            eigenvalues = np.sum(fa.components_**2, axis=1)
            variance_explained = eigenvalues / len(selected_cols) * 100
            
            return {
                'type': '因子分析',
                'variables': selected_cols,
                'n_factors': n_factors,
                'variance_explained': variance_explained.tolist(),
                'total_variance': np.sum(variance_explained),
                'status': 'completed'
            }
        except Exception as e:
            return {"error": f"因子分析失败: {str(e)}"}
    
    elif analysis_option == "方差分析":
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if not numeric_cols:
            return {"error": "方差分析需要至少一个数值型因变量"}
        if not categorical_cols:
            return {"error": "方差分析需要至少一个分类型自变量"}
        
        try:
            from scipy import stats
            import numpy as np
            
            # 自动选择第一个数值列和第一个分类列
            dependent_var = numeric_cols[0]
            independent_var = categorical_cols[0]
            
            analysis_data = data[[dependent_var, independent_var]].dropna()
            
            if len(analysis_data) < 3:
                return {"error": "样本量太小，无法进行方差分析"}
            
            # 按组分割数据
            groups = []
            group_names = []
            for group_name in analysis_data[independent_var].unique():
                group_data = analysis_data[analysis_data[independent_var] == group_name][dependent_var]
                if len(group_data) > 0:
                    groups.append(group_data)
                    group_names.append(str(group_name))
            
            if len(groups) < 2:
                return {"error": "有效组别少于2个，无法进行方差分析"}
            
            # 执行单因素方差分析
            f_stat, p_value = stats.f_oneway(*groups)
            
            return {
                'type': '方差分析',
                'dependent_var': dependent_var,
                'independent_var': independent_var,
                'f_statistic': f_stat,
                'p_value': p_value,
                'n_groups': len(groups),
                'significant': p_value < 0.05,
                'status': 'completed'
            }
        except Exception as e:
            return {"error": f"方差分析失败: {str(e)}"}
    
    return {"status": "not_implemented", "message": f"{analysis_option}功能正在开发中"}


def execute_machine_learning_single(analysis_option, processor, data):
    """执行单个机器学习分析"""
    return {"status": "not_implemented", "message": f"{analysis_option}功能正在开发中"}


def execute_time_series_single(analysis_option, processor, data):
    """执行单个时间序列分析"""
    return {"status": "not_implemented", "message": f"{analysis_option}功能正在开发中"}


def display_analysis_summary(result):
    """显示分析结果摘要"""
    if 'error' in result:
        st.error(f"错误: {result['error']}")
        return
    
    if result.get('status') == 'not_implemented':
        st.info(result.get('message', '功能正在开发中'))
        return
    
    analysis_type = result.get('type', '未知分析')
    st.write(f"**分析类型:** {analysis_type}")
    
    if analysis_type == '频数分析':
        st.write(f"**分析变量:** {result['variable']}")
        st.dataframe(result['frequency_table'].head(5))
    
    elif analysis_type == '描述统计':
        st.write(f"**分析变量:** {', '.join(result['variables'])}")
        st.dataframe(result['descriptive_stats'].head())
    
    elif analysis_type == '信度分析':
        st.write(f"**量表变量:** {', '.join(result['variables'])}")
        alpha = result['reliability_results']['cronbach_alpha']
        st.metric("克朗巴赫α系数", f"{alpha:.4f}")
    
    elif analysis_type == '线性回归':
        st.write(f"**因变量:** {result['dependent_var']}")
        st.write(f"**自变量:** {', '.join(result['independent_vars'])}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("R²", f"{result['r2_score']:.4f}")
        with col2:
            st.metric("RMSE", f"{result['rmse']:.4f}")
    
    elif analysis_type == '聚类分析':
        st.write(f"**分析变量:** {', '.join(result['variables'])}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("聚类数", result['n_clusters'])
        with col2:
            st.metric("轮廓系数", f"{result['silhouette_score']:.4f}")
        with col3:
            st.metric("样本数", result['n_samples'])
    
    elif analysis_type == '因子分析':
        st.write(f"**分析变量:** {', '.join(result['variables'])}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("因子数", result['n_factors'])
        with col2:
            st.metric("总方差解释", f"{result['total_variance']:.1f}%")
        
        # 显示各因子的方差解释
        variance_data = pd.DataFrame({
            '因子': [f"因子{i+1}" for i in range(result['n_factors'])],
            '方差解释(%)': [f"{v:.1f}" for v in result['variance_explained']]
        })
        st.dataframe(variance_data)
    
    elif analysis_type == '方差分析':
        st.write(f"**因变量:** {result['dependent_var']}")
        st.write(f"**自变量:** {result['independent_var']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("F统计量", f"{result['f_statistic']:.4f}")
        with col2:
            st.metric("p值", f"{result['p_value']:.4f}")
        with col3:
            significance = "显著" if result['significant'] else "不显著"
            st.metric("结果", significance)
    
    elif analysis_type == '数据清洗':
        col1, col2 = st.columns(2)
        with col1:
            st.metric("原始数据", f"{result['original_shape'][0]} × {result['original_shape'][1]}")
        with col2:
            st.metric("缺失值", result['missing_count'])


def display_batch_results_summary(batch_results):
    """显示批量分析结果汇总"""
    if not batch_results:
        st.info("没有分析结果")
        return
    
    # 统计信息
    total_analyses = len(batch_results)
    successful_analyses = sum(1 for result in batch_results.values() 
                             if result.get('status') == 'completed')
    failed_analyses = sum(1 for result in batch_results.values() 
                         if 'error' in result)
    
    # 显示统计
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总分析数", total_analyses)
    with col2:
        st.metric("成功完成", successful_analyses)
    with col3:
        st.metric("执行失败", failed_analyses)
    
    # 显示每个分析的结果
    for analysis_name, result in batch_results.items():
        with st.expander(f"📊 {analysis_name}"):
            display_analysis_summary(result)


def display_batch_analysis_results():
    """显示批量分析的详细结果"""
    if 'batch_analysis_results' not in st.session_state:
        return
    
    st.write("### 📋 批量分析详细结果")
    batch_results = st.session_state.batch_analysis_results
    
    # 创建标签页
    if batch_results:
        tabs = st.tabs(list(batch_results.keys()))
        
        for i, (analysis_name, result) in enumerate(batch_results.items()):
            with tabs[i]:
                display_analysis_summary(result)
                
                # 如果有详细结果，显示完整信息
                if result.get('status') == 'completed':
                    if result.get('type') == '频数分析' and 'frequency_table' in result:
                        st.write("#### 完整频数分布表")
                        st.dataframe(result['frequency_table'])
                    
                    elif result.get('type') == '描述统计' and 'descriptive_stats' in result:
                        st.write("#### 完整描述统计")
                        st.dataframe(result['descriptive_stats'])


def visualize_section():
    """数据可视化部分"""
    # 检查是否是特殊分析类型的结果展示
    if hasattr(st.session_state, 'analysis_type') and st.session_state.analysis_type in ['contrast_analysis', 'reliability_analysis', 'validity_analysis']:
        analysis_type = st.session_state.analysis_type
        
        if analysis_type == 'contrast_analysis':
            # 反差分析界面
            st.subheader("📊 反差分析")
            current_data = st.session_state.analysis_data
            
            # 选择分组列
            categorical_cols = current_data.select_dtypes(include=['object', 'category']).columns.tolist()
            group_column = st.selectbox("选择分组列", categorical_cols)
            
            # 选择数值列
            numeric_cols = current_data.select_dtypes(include=['number']).columns.tolist()
            value_columns = st.multiselect("选择要分析的数值列", numeric_cols, default=numeric_cols[:min(3, len(numeric_cols))])
            
            # 选择聚合方法
            agg_methods = ['mean', 'median', 'sum', 'std']
            agg_method = st.selectbox("选择聚合方法", agg_methods, format_func=lambda x: {'mean':'平均值', 'median':'中位数', 'sum':'总和', 'std':'标准差'}[x])
            
            if st.button("执行反差分析"):
                if not group_column or not value_columns:
                    st.error("请选择分组列和至少一个数值列")
                else:
                    with st.spinner("正在进行反差分析..."):
                        # 执行反差分析
                        processor = DataProcessor()
                        try:
                            results = processor.contrast_analysis(
                                data=current_data,
                                group_column=group_column,
                                value_columns=value_columns,
                                agg_method=agg_method
                            )
                            
                            # 显示结果
                            st.session_state.special_analysis_results = results
                            st.session_state.analysis_type = 'contrast_analysis_results'
                            st.rerun()
                        except Exception as e:
                            st.error(f"分析失败: {str(e)}")
            
        elif analysis_type in ['reliability_analysis', 'validity_analysis', 'contrast_analysis_results']:
            # 显示分析结果
            if analysis_type == 'reliability_analysis':
                st.subheader("✅ 信度分析结果")
            elif analysis_type == 'validity_analysis':
                st.subheader("✅ 效度分析结果")
            else:
                st.subheader("✅ 反差分析结果")
                
            # 显示分析结果
            if hasattr(st.session_state, 'special_analysis_results'):
                results = st.session_state.special_analysis_results
                
                # 根据分析类型显示不同的结果
                if analysis_type == 'reliability_analysis':
                    # 显示信度分析结果
                    st.write("### 克朗巴赫α系数")
                    st.info(f"α系数: {results['cronbach_alpha']:.4f}")
                    st.write(f"信度评价: {results['reliability_interpretation']}")
                    
                    st.write("### 项目间相关性")
                    st.dataframe(results['item_correlations'])
                    
                    st.write("### 项目统计")
                    st.dataframe(results['item_statistics'])
                    
                elif analysis_type == 'validity_analysis':
                    # 显示效度分析结果
                    st.write("### 结构效度 (PCA分析)")
                    st.write(f"解释方差比例: {results['pca_results']['explained_variance_ratio']:.4f}")
                    st.write(f"累积解释方差: {results['pca_results']['cumulative_variance_ratio']:.4f}")
                    
                    st.write("### 因子载荷矩阵")
                    st.dataframe(results['pca_results']['factor_loadings'])
                    
                    if 'criterion_validity' in results:
                        st.write("### 效标效度")
                        st.dataframe(results['criterion_validity'])
                    
                    st.write("### 效度解释")
                    st.info(results['validity_interpretation'])
                    
                elif analysis_type == 'contrast_analysis_results':
                    # 显示反差分析结果
                    st.write(f"### 分组统计 ({results['agg_method']})")
                    st.dataframe(results['group_statistics'])
                    
                    st.write("### 组间差异")
                    st.dataframe(results['group_differences'])
                    
                    st.write("### 总体统计")
                    st.dataframe(results['overall_statistics'])
                    
                    st.write("### 变异系数")
                    st.dataframe(results['coefficient_of_variation'])
            
            # 返回按钮
            if st.button("返回分析选择"):
                if hasattr(st.session_state, 'analysis_type'):
                    del st.session_state.analysis_type
                if hasattr(st.session_state, 'special_analysis_results'):
                    del st.session_state.special_analysis_results
                st.session_state.current_step = 'analyze'
                st.rerun()
    else:
        # 常规可视化逻辑
        st.subheader("📈 数据可视化")
        
        # 检查是否有数据
        if st.session_state.data is None:
            st.error("请先上传数据!")
            if st.button("返回上传"):
                st.session_state.current_step = 'upload'
                st.rerun()
            return
        
        # 获取当前数据：优先使用已处理的数据（如果存在且不为 None），否则使用原始上传的数据
        if 'processed_data' in st.session_state and st.session_state.processed_data is not None:
            current_data = st.session_state.processed_data
        else:
            current_data = st.session_state.data
        
        # 二次检查确保current_data不为None
        if current_data is None:
            st.error("数据加载失败，请重新上传数据!")
            if st.button("返回上传"):
                st.session_state.current_step = 'upload'
                st.rerun()
            return
        
        # 创建可视化管理器
        viz_manager = create_visualization_manager()
        
        # 可视化类型选择
        st.write("### 🎨 可视化选项")
        viz_option = st.radio(
            "选择可视化模式",
            ["智能推荐可视化", "自定义可视化", "交互式图表"]
        )
    
    # 智能推荐可视化
    if viz_option == "智能推荐可视化":
        st.write("#### 🤖 系统推荐图表")
        
        with st.spinner("正在分析数据并生成推荐图表..."):
            # 获取数据特征
            data_features = {}
            data_features['numeric_columns'] = list(current_data.select_dtypes(include=['number']).columns)
            data_features['categorical_columns'] = list(current_data.select_dtypes(include=['object', 'category']).columns)
            
            # 检测日期列
            date_columns = []
            for col in current_data.columns:
                if pd.api.types.is_datetime64_any_dtype(current_data[col]):
                    date_columns.append(col)
                elif 'date' in col.lower() or 'time' in col.lower():
                    try:
                        current_data[col] = pd.to_datetime(current_data[col])
                        date_columns.append(col)
                    except:
                        pass
            data_features['date_columns'] = date_columns
            
            # 生成推荐图表
            recommended_charts = viz_manager.get_recommended_charts(current_data, data_features)
            
            # 显示图表
            if recommended_charts:
                st.success(f"已生成 {len(recommended_charts)} 个推荐图表")
                
                # 保存到会话状态供报告使用
                st.session_state.recommended_charts = recommended_charts
                
                # 展示图表
                for chart_name, fig in recommended_charts.items():
                    with st.expander(f"📈 {chart_name}"):
                        safe_display_figure(fig)
            else:
                st.warning("无法生成推荐图表，请尝试自定义可视化")
    
    # 自定义可视化
    elif viz_option == "自定义可视化":
        st.write("#### 🎛️ 自定义图表")
        
        chart_type = st.selectbox(
            "选择图表类型",
            ["柱状图", "折线图", "散点图", "直方图", "箱线图", "饼图", "热力图"]
        )
        
        # 获取列类型
        numeric_columns = list(current_data.select_dtypes(include=['number']).columns)
        categorical_columns = list(current_data.select_dtypes(include=['object', 'category']).columns)
        all_columns = numeric_columns + categorical_columns
        
        # 根据图表类型显示不同的选项
        if chart_type == "柱状图":
            if categorical_columns and numeric_columns:
                x_col = st.selectbox("选择X轴（分类变量）", categorical_columns)
                y_col = st.selectbox("选择Y轴（数值变量）", numeric_columns)
                
                # 聚合方法
                agg_method = st.selectbox("聚合方法", ["均值", "总和", "计数"])
                
                # 排序方式
                sort_by = st.selectbox("排序方式", ["默认顺序", "Y轴值升序", "Y轴值降序"])
                
                if st.button("生成柱状图"):
                    # 数据聚合
                    if agg_method == "均值":
                        agg_data = current_data.groupby(x_col)[y_col].mean().reset_index()
                    elif agg_method == "总和":
                        agg_data = current_data.groupby(x_col)[y_col].sum().reset_index()
                    else:
                        agg_data = current_data.groupby(x_col).size().reset_index(name=y_col)
                    
                    # 排序
                    if sort_by == "Y轴值升序":
                        agg_data = agg_data.sort_values(y_col)
                    elif sort_by == "Y轴值降序":
                        agg_data = agg_data.sort_values(y_col, ascending=False)
                    
                    # 创建图表
                    visualizer = viz_manager.visualizer
                    fig = visualizer.create_bar_chart(
                        agg_data, x_col, y_col, 
                        title=f"{y_col} by {x_col} ({agg_method})")
                    
                    safe_display_figure(fig)
                    
                    # 保存到会话状态
                    if 'custom_charts' not in st.session_state:
                        st.session_state.custom_charts = {}
                    st.session_state.custom_charts["柱状图"] = fig
            else:
                st.warning("需要至少一个分类列和一个数值列来创建柱状图")
        
        elif chart_type == "折线图":
            if len(numeric_columns) >= 2:
                x_col = st.selectbox("选择X轴", numeric_columns)
                y_cols = st.multiselect("选择Y轴（可多选）", numeric_columns, default=[numeric_columns[0]])
                
                if st.button("生成折线图"):
                    visualizer = viz_manager.visualizer
                    fig = visualizer.create_line_chart(
                        current_data, x_col, y_cols,
                        title=f"折线图: {', '.join(y_cols)} vs {x_col}")
                    
                    safe_display_figure(fig)
                    
                    # 保存到会话状态
                    if 'custom_charts' not in st.session_state:
                        st.session_state.custom_charts = {}
                    st.session_state.custom_charts["折线图"] = fig
            else:
                st.warning("需要至少两个数值列来创建折线图")
        
        elif chart_type == "散点图":
            if len(numeric_columns) >= 2:
                x_col = st.selectbox("选择X轴", numeric_columns)
                y_col = st.selectbox("选择Y轴", numeric_columns)
                
                # 可选参数
                show_trendline = st.checkbox("显示趋势线", value=False)
                
                hue_col = None
                if categorical_columns:
                    if st.checkbox("按分类着色", value=False):
                        hue_col = st.selectbox("选择分类列", categorical_columns)
                
                if st.button("生成散点图"):
                    visualizer = viz_manager.visualizer
                    fig = visualizer.create_scatter_plot(
                        current_data, x_col, y_col,
                        title=f"散点图: {y_col} vs {x_col}",
                        trendline=show_trendline,
                        hue=hue_col)
                    
                    safe_display_figure(fig)
                    
                    # 保存到会话状态
                    if 'custom_charts' not in st.session_state:
                        st.session_state.custom_charts = {}
                    st.session_state.custom_charts["散点图"] = fig
            else:
                st.warning("需要至少两个数值列来创建散点图")
        
        elif chart_type == "直方图":
            if numeric_columns:
                x_col = st.selectbox("选择要分析的列", numeric_columns)
                bins = st.slider("直方图柱数", min_value=5, max_value=100, value=30)
                show_kde = st.checkbox("显示密度曲线", value=True)
                
                if st.button("生成直方图"):
                    visualizer = viz_manager.visualizer
                    fig = visualizer.create_histogram(
                        current_data, x_col, bins=bins, kde=show_kde,
                        title=f"{x_col}的分布")
                    
                    safe_display_figure(fig)
                    
                    # 保存到会话状态
                    if 'custom_charts' not in st.session_state:
                        st.session_state.custom_charts = {}
                    st.session_state.custom_charts["直方图"] = fig
            else:
                st.warning("需要至少一个数值列来创建直方图")
        
        elif chart_type == "箱线图":
            if numeric_columns:
                y_col = st.selectbox("选择数值列", numeric_columns)
                
                x_col = None
                if categorical_columns:
                    if st.checkbox("按分类分组", value=False):
                        x_col = st.selectbox("选择分类列", categorical_columns)
                
                if st.button("生成箱线图"):
                    visualizer = viz_manager.visualizer
                    fig = visualizer.create_box_plot(
                        current_data, x_col, y_col,
                        title=f"{y_col}的箱线图" + (f" by {x_col}" if x_col else ""))
                    
                    safe_display_figure(fig)
                    
                    # 保存到会话状态
                    if 'custom_charts' not in st.session_state:
                        st.session_state.custom_charts = {}
                    st.session_state.custom_charts["箱线图"] = fig
            else:
                st.warning("需要至少一个数值列来创建箱线图")
        
        elif chart_type == "饼图":
            if categorical_columns:
                category_col = st.selectbox("选择分类列", categorical_columns)
                
                # 可选参数
                top_n = st.slider("显示前N个类别", min_value=1, max_value=20, value=10)
                
                if st.button("生成饼图"):
                    # 计算频率
                    freq_data = current_data[category_col].value_counts().reset_index()
                    freq_data.columns = [category_col, 'count']
                    
                    visualizer = viz_manager.visualizer
                    fig = visualizer.create_pie_chart(
                        freq_data, 'count', category_col,
                        title=f"{category_col}的分布",
                        top_n=top_n)
                    
                    safe_display_figure(fig)
                    
                    # 保存到会话状态
                    if 'custom_charts' not in st.session_state:
                        st.session_state.custom_charts = {}
                    st.session_state.custom_charts["饼图"] = fig
            else:
                st.warning("需要至少一个分类列来创建饼图")
        
        elif chart_type == "热力图":
            if len(numeric_columns) >= 2:
                selected_cols = st.multiselect(
                    "选择要包含在热力图中的列",
                    numeric_columns,
                    default=numeric_columns[:min(5, len(numeric_columns))]
                )
                
                if len(selected_cols) >= 2:
                    if st.button("生成热力图"):
                        subset_data = current_data[selected_cols]
                        
                        visualizer = viz_manager.visualizer
                        fig = visualizer.create_heatmap(
                            subset_data,
                            title="特征相关性热力图")
                        
                        safe_display_figure(fig)
                        
                        # 保存到会话状态
                        if 'custom_charts' not in st.session_state:
                            st.session_state.custom_charts = {}
                        st.session_state.custom_charts["热力图"] = fig
                else:
                    st.warning("需要至少选择两个列")
            else:
                st.warning("需要至少两个数值列来创建热力图")
    
    # 交互式图表
    elif viz_option == "交互式图表":
        st.write("#### 🔄 交互式图表")
        st.info("交互式图表支持缩放、悬停查看详细信息等功能")
        
        # 获取列类型
        numeric_columns = list(current_data.select_dtypes(include=['number']).columns)
        categorical_columns = list(current_data.select_dtypes(include=['object', 'category']).columns)
        
        interactive_type = st.selectbox(
            "选择交互式图表类型",
            ["交互式散点图", "交互式直方图"]
        )
        
        if interactive_type == "交互式散点图":
            if len(numeric_columns) >= 2:
                x_col = st.selectbox("选择X轴", numeric_columns)
                y_col = st.selectbox("选择Y轴", numeric_columns)
                
                # 可选参数
                color_col = None
                if categorical_columns:
                    if st.checkbox("按分类着色", value=False):
                        color_col = st.selectbox("选择颜色列", categorical_columns)
                
                if st.button("生成交互式散点图"):
                    visualizer = viz_manager.visualizer
                    fig = visualizer.create_interactive_scatter(
                        current_data, x_col, y_col,
                        title=f"交互式散点图: {y_col} vs {x_col}",
                        color=color_col
                    )
                    
                    st.plotly_chart(fig)
            else:
                st.warning("需要至少两个数值列")
        
        elif interactive_type == "交互式直方图":
            if numeric_columns:
                x_col = st.selectbox("选择要分析的列", numeric_columns)
                
                color_col = None
                if categorical_columns:
                    if st.checkbox("按分类着色", value=False):
                        color_col = st.selectbox("选择颜色列", categorical_columns)
                
                if st.button("生成交互式直方图"):
                    visualizer = viz_manager.visualizer
                    fig = visualizer.create_interactive_histogram(
                        current_data, x_col,
                        title=f"交互式直方图: {x_col}的分布",
                        color=color_col
                    )
                    
                    st.plotly_chart(fig)
            else:
                st.warning("需要至少一个数值列")
    
    # 导航按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏪ 返回数据分析", use_container_width=True):
            st.session_state.current_step = "analyze"
            st.rerun()
    
    with col2:
        if st.button("⏩ 生成报告", use_container_width=True):
            st.session_state.current_step = "report"
            st.rerun()


def report_section():
    """报告生成部分"""
    st.subheader("📄 报告生成")
    
    # 检查是否有数据
    if st.session_state.data is None:
        st.error("请先上传数据!")
        if st.button("返回上传"):
            st.session_state.current_step = 'upload'
            st.rerun()
        return
    
    # 使用处理后的数据或原始数据
    current_data = st.session_state.processed_data if st.session_state.processed_data is not None else st.session_state.data
    
    # 报告设置
    st.subheader("报告设置")
    
    # 基本信息设置
    col1, col2 = st.columns(2)
    with col1:
        report_title = st.text_input("报告标题", value=f"数据分析报告 - {st.session_state.file_name if hasattr(st.session_state, 'file_name') and st.session_state.file_name else '数据集'}")
    with col2:
        report_author = st.text_input("报告作者", value="AI数据分析系统")
    
    # 报告模板选项（新增）
    st.subheader("📋 报告模板选项")
    include_template = st.checkbox("包含报告样例模板", value=True, 
                                  help="在报告开头添加标准化的报告模板示例，展示专业的报告结构")
    
    # 问卷数据智能整合（新增）
    st.subheader("🧠 问卷数据智能整合")
    enable_smart_merge = st.checkbox("启用问卷数据智能分析", value=True,
                                   help="系统将自动识别问卷题项类型，检测量表结构，并生成专门的问卷分析章节")
    
    # 题项映射设置
    item_mapping = None
    if enable_smart_merge:
        st.write("**题项映射设置**")
        mapping_option = st.radio(
            "选择题项映射方式：",
            ["自动智能识别", "手动指定映射", "上传题项对照表"],
            help="自动识别：系统智能推断列名含义；手动指定：自定义题项描述；上传对照表：使用外部映射文件"
        )
        
        if mapping_option == "手动指定映射":
            st.write("为数据列指定题项描述：")
            item_mapping = {}
            
            # 只显示前10个列以避免界面过于复杂
            columns_to_show = current_data.columns[:10].tolist()
            if len(current_data.columns) > 10:
                st.info(f"显示前10个列的映射设置，共有 {len(current_data.columns)} 列")
            
            for i, col in enumerate(columns_to_show):
                col_key = f"item_mapping_{i}"
                description = st.text_input(f"列 '{col}' 的题项描述：", 
                                          value=f"题项: {col}", 
                                          key=col_key)
                if description.strip():
                    item_mapping[col] = description.strip()
        
        elif mapping_option == "上传题项对照表":
            st.write("上传CSV格式的题项对照表，包含'列名'和'题项描述'两列：")
            mapping_file = st.file_uploader("选择题项对照表文件", type=['csv'], key="mapping_file")
            
            if mapping_file is not None:
                try:
                    import io
                    mapping_df = pd.read_csv(io.StringIO(mapping_file.getvalue().decode("utf-8")))
                    
                    if '列名' in mapping_df.columns and '题项描述' in mapping_df.columns:
                        item_mapping = dict(zip(mapping_df['列名'], mapping_df['题项描述']))
                        st.success(f"成功加载 {len(item_mapping)} 个题项映射")
                        
                        # 显示映射预览
                        st.write("**映射预览：**")
                        preview_df = mapping_df.head(5)
                        st.dataframe(preview_df, use_container_width=True)
                    else:
                        st.error("对照表必须包含'列名'和'题项描述'两列")
                except Exception as e:
                    st.error(f"读取题项对照表失败：{str(e)}")
    
    # 报告内容选择
    st.subheader("报告内容选择")
    
    # 选择要包含的内容部分
    include_executive_summary = st.checkbox("执行摘要", value=True)
    include_data_overview = st.checkbox("数据概览", value=True)
    include_preprocessing = st.checkbox("数据预处理", value=True)
    include_analysis_results = st.checkbox("分析结果", value=True)
    include_visualizations = st.checkbox("数据可视化", value=True)
    include_conclusion = st.checkbox("结论与建议", value=True)
    
    # 高级分析结果选项（新增）
    if include_analysis_results:
        st.write("**包含的分析类型：**")
        col1, col2 = st.columns(2)
        with col1:
            include_descriptive = st.checkbox("描述性统计", value=True)
            include_correlation = st.checkbox("相关性分析", value=True)
            include_cluster = st.checkbox("聚类分析", value=True)
        with col2:
            include_factor = st.checkbox("因子分析", value=True)
            include_anova = st.checkbox("方差分析", value=True)
            include_models = st.checkbox("模型推荐", value=True)
    
    # 自定义输出路径
    custom_output_path = st.checkbox("自定义输出路径")
    output_path = None
    if custom_output_path:
        default_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = st.text_input("输出路径", value=default_path)
    
    # 生成报告按钮
    if st.button("🚀 生成智能分析报告", use_container_width=True):
        try:
            with st.spinner("正在生成智能分析报告..."):
                # 创建AI增强器（如果启用）
                ai_enhancer = None
                if (st.session_state.ai_enhancement_enabled and 
                    AI_ENHANCEMENT_AVAILABLE and
                    (st.session_state.ai_api_key or st.session_state.ai_provider == "local")):
                    
                    try:
                        config = AIModelConfig(
                            provider=st.session_state.ai_provider,
                            model_name=st.session_state.ai_model,
                            api_key=st.session_state.ai_api_key if st.session_state.ai_api_key else None,
                            api_base=st.session_state.ai_api_base if st.session_state.ai_api_base else None
                        )
                        ai_enhancer = AIReportEnhancer(config)
                        st.info("🤖 AI报告增强已启用")
                    except Exception as e:
                        st.warning(f"⚠️ AI增强器初始化失败: {str(e)}，将使用普通报告生成")
                        ai_enhancer = None
                
                # 创建高级报告生成器（带AI增强）
                report_gen = create_advanced_report_generator()
                if ai_enhancer:
                    report_gen.set_ai_enhancer(ai_enhancer)
                
                # 准备分析结果
                analysis_results = st.session_state.analysis_results.copy() if hasattr(st.session_state, 'analysis_results') else {}
                
                # 过滤分析结果（根据用户选择）
                if include_analysis_results:
                    filtered_results = {}
                    if include_descriptive and 'descriptive_stats' in analysis_results:
                        filtered_results['descriptive_stats'] = analysis_results['descriptive_stats']
                    if include_correlation and 'correlation' in analysis_results:
                        filtered_results['correlation'] = analysis_results['correlation']
                    if include_cluster and 'cluster_analysis' in analysis_results:
                        filtered_results['cluster_analysis'] = analysis_results['cluster_analysis']
                    if include_factor and 'factor_analysis' in analysis_results:
                        filtered_results['factor_analysis'] = analysis_results['factor_analysis']
                    if include_anova and 'anova_analysis' in analysis_results:
                        filtered_results['anova_analysis'] = analysis_results['anova_analysis']
                    if include_models and 'model_recommendations' in analysis_results:
                        filtered_results['model_recommendations'] = analysis_results['model_recommendations']
                    
                    analysis_results = filtered_results
                
                # 添加预处理信息
                if hasattr(st.session_state, 'preprocessing_info') and st.session_state.preprocessing_info:
                    analysis_results['preprocessing'] = st.session_state.preprocessing_info
                
                # 准备可视化图表
                charts = {}
                if include_visualizations:
                    # 收集所有可用图表
                    if hasattr(st.session_state, 'recommended_charts') and st.session_state.recommended_charts:
                        charts.update(st.session_state.recommended_charts)
                    if hasattr(st.session_state, 'custom_charts') and st.session_state.custom_charts:
                        charts.update(st.session_state.custom_charts)
                
                # 如果选择了自定义输出路径
                if custom_output_path and output_path:
                    # 确保目录存在
                    os.makedirs(output_path, exist_ok=True)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"{report_title.replace(' ', '_')}_{timestamp}.docx"
                    full_output_path = os.path.join(output_path, filename)
                else:
                    full_output_path = None
                
                # 生成报告
                # 安全地传递charts参数，确保即使为空也不会导致NoneType迭代错误
                charts_to_use = charts if include_visualizations and charts else {}
                saved_path = report_gen.generate_full_report(
                    data=current_data,
                    analysis_results=analysis_results,
                    charts=charts_to_use,
                    file_info={
                        'file_name': st.session_state.file_name if hasattr(st.session_state, 'file_name') else '未知',
                        'file_format': st.session_state.file_format if hasattr(st.session_state, 'file_format') else '未知'
                    },
                    output_path=full_output_path,
                    include_template=include_template,
                    item_mapping=item_mapping if enable_smart_merge else None
                )
                
                # 保存报告路径到会话状态
                st.session_state.report_path = saved_path
                
                # 更新进度
                st.session_state.progress = 100
                
                st.success(f"智能分析报告已成功生成并保存至：{saved_path}")
                
                # 显示报告信息
                st.info("报告特色功能：")
                features = []
                if include_template:
                    features.append("✅ 包含专业报告模板示例")
                if enable_smart_merge:
                    features.append("✅ 智能问卷数据分析")
                if item_mapping:
                    features.append(f"✅ 自定义题项映射 ({len(item_mapping)} 个题项)")
                if len(analysis_results) > 2:
                    features.append(f"✅ 完整统计分析 ({len(analysis_results)} 种分析类型)")
                if charts_to_use:
                    features.append(f"✅ 数据可视化图表 ({len(charts_to_use)} 个图表)")
                
                for feature in features:
                    st.write(feature)
                
        except Exception as e:
            st.error(f"生成报告时出现错误：{str(e)}")
            logger.exception("报告生成失败")
    
    # 显示已生成的报告信息
    if hasattr(st.session_state, 'report_path') and st.session_state.report_path:
        st.subheader("报告已生成")
        st.info(f"报告路径: {st.session_state.report_path}")
        
        # 提供下载链接（如果可能）
        try:
            with open(st.session_state.report_path, "rb") as file:
                st.download_button(
                    label="下载报告",
                    data=file,
                    file_name=os.path.basename(st.session_state.report_path),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        except:
            st.info("请在文件资源管理器中打开报告文件")
    
    # 导航按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 返回数据可视化", use_container_width=True):
            st.session_state.current_step = 'visualize'
            st.rerun()
    with col2:
        if st.button("🔄 重新开始", use_container_width=True):
            # 重置所有会话状态
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.current_step = 'upload'
            st.rerun()


def show_progress():
    """
    显示进度条和状态信息
    """
    with st.sidebar:
        # 标题和说明
        st.markdown("### 📊 处理进度跟踪")
        st.markdown("---")
        
        # 总进度条
        st.markdown("**总体进度**")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(st.session_state.progress)
        with col2:
            st.markdown(f"**{st.session_state.progress}%**")
        
        st.markdown("---")
        
        # 步骤进度
        st.markdown("**步骤进度**")
        
        # 定义步骤信息
        steps = [
            {'id': 'upload', 'name': '数据上传', 'icon': '📁', 'status': 'completed' if st.session_state.current_step != 'upload' else 'active'},
            {'id': 'analyze', 'name': '数据分析', 'icon': '🔍', 'status': 'completed' if st.session_state.current_step not in ['upload', 'analyze'] else 'active' if st.session_state.current_step == 'analyze' else 'pending'},
            {'id': 'visualize', 'name': '数据可视化', 'icon': '📊', 'status': 'completed' if st.session_state.current_step == 'report' else 'active' if st.session_state.current_step == 'visualize' else 'pending'},
            {'id': 'report', 'name': '报告生成', 'icon': '📑', 'status': 'active' if st.session_state.current_step == 'report' else 'pending'}
        ]
        
        # 显示步骤进度
        for i, step in enumerate(steps):
            # 状态图标
            status_icon = {
                'completed': '✅',
                'active': '🔄',
                'pending': '⏳'
            }.get(step['status'], '⏳')
            
            # 状态文本颜色
            status_color = {
                'completed': '#28a745',  # 绿色
                'active': '#007bff',    # 蓝色
                'pending': '#6c757d'    # 灰色
            }.get(step['status'], '#6c757d')
            
            # 显示步骤
            st.markdown(
                f"<div style='display: flex; align-items: center; margin-bottom: 8px;'>"  
                f"  <span style='font-size: 16px; margin-right: 8px;'>{status_icon}</span>"  
                f"  <span style='font-weight: bold; color: {status_color};'>{step['icon']} {step['name']}</span>"  
                f"</div>",
                unsafe_allow_html=True
            )
            
            # 添加连接线（除了最后一个步骤）
            if i < len(steps) - 1:
                st.markdown("<div style='margin-left: 8px; height: 12px; border-left: 2px dashed #ddd;'></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 状态信息面板
        st.markdown("**状态信息**")
        status_panel = st.empty()
        
        # 根据当前步骤显示不同的状态信息
        status_info = []
        
        # 数据状态
        if st.session_state.data is not None:
            data_status = "✅ 已加载"
            data_details = f"📋 {len(st.session_state.data)} 行 × {len(st.session_state.data.columns)} 列"
        else:
            data_status = "⏳ 未加载"
            data_details = "📋 请上传数据文件"
        
        status_info.append(f"**数据状态**: {data_status}")
        status_info.append(f"{data_details}")
        
        # 处理状态
        if st.session_state.processed_data is not None:
            process_status = "✅ 已处理"
        elif st.session_state.data is not None:
            process_status = "⏳ 待处理"
        else:
            process_status = "🔒 未开始"
        
        status_info.append(f"**处理状态**: {process_status}")
        
        # 可视化状态
        viz_count = 0
        if hasattr(st.session_state, 'recommended_charts') and st.session_state.recommended_charts:
            viz_count += len(st.session_state.recommended_charts)
        if hasattr(st.session_state, 'custom_charts') and st.session_state.custom_charts:
            viz_count += len(st.session_state.custom_charts)
            
        if viz_count > 0:
            viz_status = f"✅ 已生成 ({viz_count} 个图表)"
        elif st.session_state.data is not None:
            viz_status = "⏳ 待生成"
        else:
            viz_status = "🔒 未开始"
        
        status_info.append(f"**可视化状态**: {viz_status}")
        
        # 报告状态
        if hasattr(st.session_state, 'report_path') and st.session_state.report_path:
            report_status = "✅ 已生成"
        elif st.session_state.data is not None:
            report_status = "⏳ 待生成"
        else:
            report_status = "🔒 未开始"
        
        status_info.append(f"**报告状态**: {report_status}")
        
        # 显示状态信息
        status_panel.markdown("\n".join(status_info))
        
        st.markdown("---")
        
        # 系统信息
        st.markdown("**系统信息**")
        st.markdown("🤖 AI智能数据分析系统 v1.0")
        st.markdown("📅 实时处理与分析")


def ai_assistant_section():
    """
    AI智能助手部分
    """
    if not st.session_state.show_ai_assistant:
        return
    
    with st.sidebar:
        st.markdown("## 💬 AI智能助手")
        st.markdown("有任何数据分析问题，随时向我提问！")
        
        # 显示对话历史
        chat_container = st.container(height=300)
        
        # 显示历史对话
        with chat_container:
            if st.session_state.conversation_history:
                for message in st.session_state.conversation_history:
                    if message['role'] == 'user':
                        st.markdown(f"**👤 您:** {message['content']}")
                    else:
                        st.markdown(f"**🤖 AI:** {message['content']}")
                        st.markdown("---")
            else:
                st.markdown("**🤖 AI:** 您好！我是您的数据分析助手。请问有什么可以帮助您的？")
        
        # 用户输入
        user_query = st.text_input("请输入您的问题或指令:", placeholder="例如：解释什么是相关性分析？")
        
        if st.button("发送", use_container_width=True):
            if user_query.strip():
                # 添加用户消息到历史
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': user_query.strip()
                })
                
                # 生成AI响应
                with st.spinner("AI正在思考..."):
                    # 获取相关数据和分析结果
                    data = st.session_state.processed_data if st.session_state.processed_data is not None else st.session_state.data
                    analysis_results = st.session_state.analysis_results
                    
                    # 生成响应
                    response = st.session_state.ai_assistant.generate_response(
                        user_query.strip(),
                        data=data,
                        analysis_results=analysis_results
                    )
                    
                    # 添加AI回复到历史
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                
                # 限制对话历史长度
                if len(st.session_state.conversation_history) > 10:
                    st.session_state.conversation_history = st.session_state.conversation_history[-10:]
                
                # 重新运行应用以更新UI
                st.rerun()
        
        # 清除对话历史
        if st.button("清除历史", use_container_width=True, type="secondary"):
            st.session_state.conversation_history = []
            st.rerun()

def ai_enhancement_sidebar():
    """显示AI增强配置侧边栏"""
    if not AI_ENHANCEMENT_AVAILABLE:
        return
        
    with st.sidebar:
        st.markdown("### 🤖 AI报告增强")
        
        # 启用/禁用AI增强
        ai_enabled = st.checkbox(
            "启用AI报告增强",
            value=st.session_state.ai_enhancement_enabled,
            help="使用AI大模型对分析结果进行深度解读和洞察"
        )
        st.session_state.ai_enhancement_enabled = ai_enabled
        
        if ai_enabled:
            # AI提供商选择
            ai_provider = st.selectbox(
                "AI提供商",
                options=["openai", "qwen", "chatglm", "local"],
                index=["openai", "qwen", "chatglm", "local"].index(st.session_state.ai_provider),
                help="选择AI模型提供商"
            )
            st.session_state.ai_provider = ai_provider
            
            # 模型选择
            if ai_provider == "openai":
                model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
                default_model = "gpt-3.5-turbo"
            elif ai_provider == "qwen":
                model_options = ["qwen-turbo", "qwen-plus", "qwen-max"]
                default_model = "qwen-turbo"
            elif ai_provider == "chatglm":
                model_options = ["chatglm3-6b", "chatglm4"]
                default_model = "chatglm3-6b"
            else:  # local
                model_options = ["llama2", "llama3", "qwen2", "chatglm3"]
                default_model = "llama2"
            
            ai_model = st.selectbox(
                "AI模型",
                options=model_options,
                index=model_options.index(st.session_state.ai_model) if st.session_state.ai_model in model_options else 0
            )
            st.session_state.ai_model = ai_model
            
            # API配置
            if ai_provider != "local":
                api_key = st.text_input(
                    "API密钥",
                    value=st.session_state.ai_api_key,
                    type="password",
                    help="输入AI服务的API密钥"
                )
                st.session_state.ai_api_key = api_key
                
                api_base = st.text_input(
                    "API基础URL (可选)",
                    value=st.session_state.ai_api_base,
                    help="自定义API基础URL，留空使用默认"
                )
                st.session_state.ai_api_base = api_base
            else:
                api_base = st.text_input(
                    "本地模型API地址",
                    value=st.session_state.ai_api_base or "http://localhost:11434/api/generate",
                    help="本地模型API地址，如Ollama"
                )
                st.session_state.ai_api_base = api_base
            
            # 增强类型选择
            enhancement_type = st.selectbox(
                "增强类型",
                options=["comprehensive", "insights", "recommendations", "interpretation"],
                index=["comprehensive", "insights", "recommendations", "interpretation"].index(st.session_state.ai_enhancement_type),
                help="选择AI增强的重点方向"
            )
            st.session_state.ai_enhancement_type = enhancement_type
            
            # 增强类型说明
            enhancement_descriptions = {
                "comprehensive": "🎯 **综合分析**: 全面的洞察、建议和解释",
                "insights": "🔍 **深度洞察**: 专注于数据模式和趋势发现",
                "recommendations": "💡 **行动建议**: 基于分析结果提供具体建议",
                "interpretation": "📖 **结果解读**: 用通俗语言解释统计结果"
            }
            st.markdown(enhancement_descriptions[enhancement_type])
            
            # 测试连接按钮
            if st.button("🔧 测试AI连接", use_container_width=True):
                test_ai_connection()

def test_ai_connection():
    """测试AI连接"""
    try:
        if not st.session_state.ai_api_key and st.session_state.ai_provider != "local":
            st.error("请先输入API密钥")
            return
            
        with st.spinner("正在测试AI连接..."):
            # 创建AI增强器
            config = AIModelConfig(
                provider=st.session_state.ai_provider,
                model_name=st.session_state.ai_model,
                api_key=st.session_state.ai_api_key,
                api_base=st.session_state.ai_api_base if st.session_state.ai_api_base else None
            )
            
            enhancer = AIReportEnhancer(config)
            
            # 进行简单测试
            test_prompt = "这是一个测试消息，请回复'测试成功'"
            response = enhancer._call_ai_model(test_prompt)
            
            if response:
                st.success(f"✅ AI连接测试成功！\n回复: {response[:100]}...")
            else:
                st.error("❌ AI连接测试失败，请检查配置")
                
    except Exception as e:
        # 显示详细错误信息
        st.error(f"❌ AI连接测试失败: {str(e)}")
        
        # 在expander中显示更详细的调试信息
        with st.expander("🔍 详细错误信息 (调试用)", expanded=False):
            st.code(f"""
错误类型: {type(e).__name__}
错误信息: {str(e)}
配置信息:
  - 提供商: {st.session_state.get('ai_provider', '未设置')}
  - 模型: {st.session_state.get('ai_model', '未设置')}
  - API密钥: {'已设置' if st.session_state.get('ai_api_key') else '未设置'}
  - API地址: {st.session_state.get('ai_api_base', '默认地址')}

调试建议:
1. 检查网络连接是否正常
2. 确认API密钥是否正确
3. 验证API地址是否可访问
4. 检查防火墙设置
            """, language="text")
            
        # 提供常见问题解决方案
        st.info("""
        **常见问题解决方案:**
        
        🔗 **连接错误 (Connection error)**
        - 检查网络连接
        - 确认API地址是否正确
        - 检查是否需要代理设置
        
        🔑 **认证错误 (Authentication failed)**
        - 验证API密钥是否正确
        - 检查API密钥是否有效期内
        - 确认密钥权限是否足够
        
        ⏱️ **超时错误 (Timeout)**
        - 检查网络速度
        - 考虑增加超时时间
        - 尝试更换网络环境
        
        📊 **配额错误 (Rate limit/Quota exceeded)**
        - 检查API使用配额
        - 等待配额重置
        - 升级API套餐
        """)

def run_app():
    """运行Streamlit应用"""
    try:
        # 设置页面配置
        set_page_config()
        
        # 初始化会话状态
        AppState.initialize_session_state()
        
        # 显示进度条和状态信息
        show_progress()
        
        # 显示AI助手
        ai_assistant_section()
        
        # 显示AI增强配置
        ai_enhancement_sidebar()
        
        # 显示标题
        display_header()
        
        # 根据当前步骤显示相应内容
        if st.session_state.current_step == 'upload':
            file_upload_section()
        elif st.session_state.current_step == 'analyze':
            analyze_section()
        elif st.session_state.current_step == 'visualize':
            visualize_section()
        elif st.session_state.current_step == 'report':
            report_section()
        
        # 显示页脚
        st.markdown("""
        <hr>
        <div style='text-align: center; color: #7f8c8d;'>
            <p>© 2025 AI数据分析大模型系统 | 版本 1.0.0</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"应用运行出错: {str(e)}")
        logger.error(f"应用运行出错: {str(e)}", exc_info=True)


if __name__ == "__main__":
    run_app()