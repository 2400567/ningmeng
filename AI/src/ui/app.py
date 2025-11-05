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
    """数据分析部分"""
    st.subheader("🔍 数据处理与智能分析")
    
    # 检查是否有数据
    if st.session_state.data is None:
        st.error("请先上传数据!")
        if st.button("返回上传"):
            st.session_state.current_step = 'upload'
            st.rerun()
        return
    
    # 创建数据处理器实例
    processor = DataProcessor()
    
    # 数据清洗部分
    with st.expander("🔧 数据清洗", expanded=True):
        st.write("### 数据清洗设置")
        
        # 处理缺失值
        st.write("#### 缺失值处理")
        missing_strategy = st.selectbox(
            "选择缺失值处理策略",
            options=["不处理", "均值填充", "中位数填充", "众数填充", "删除含缺失值的行", "KNN填充"],
            index=1
        )
        
        # 处理异常值
        st.write("#### 异常值处理")
        handle_outliers = st.checkbox("启用异常值检测和处理", value=True)
        if handle_outliers:
            outlier_method = st.selectbox(
                "选择异常值检测方法",
                options=["Z-score法", "IQR法", "百分位数法"],
                index=0
            )
            outlier_threshold = st.slider(
                "异常值阈值", 
                min_value=1.0, 
                max_value=5.0, 
                value=3.0, 
                step=0.1
            )
        
        # 删除重复值
        remove_dups = st.checkbox("删除重复行", value=True)
        
        # 应用清洗
        if st.button("应用数据清洗"):
            with st.spinner("正在进行数据清洗..."):
                try:
                    # 创建数据副本
                    cleaned_data = st.session_state.data.copy()
                    
                    # 应用缺失值处理
                    if missing_strategy != "不处理":
                        strategy_map = {
                            "均值填充": "mean",
                            "中位数填充": "median",
                            "众数填充": "mode",
                            "删除含缺失值的行": "drop",
                            "KNN填充": "knn"
                        }
                        cleaned_data = processor.handle_missing_values(
                            cleaned_data, 
                            strategy=strategy_map[missing_strategy]
                        )
                    
                    # 应用异常值处理
                    if handle_outliers:
                        method_map = {
                            "Z-score法": "zscore",
                            "IQR法": "iqr",
                            "百分位数法": "percentile"
                        }
                        cleaned_data = processor.handle_outliers(
                            cleaned_data, 
                            method=method_map[outlier_method],
                            threshold=outlier_threshold
                        )
                    
                    # 删除重复值
                    if remove_dups:
                        cleaned_data = processor.remove_duplicates(cleaned_data)
                    
                    # 更新会话状态
                    st.session_state.processed_data = cleaned_data
                    st.success(f"数据清洗完成！处理后数据形状: {cleaned_data.shape}")
                    
                    # 显示处理前后对比
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**处理前:**")
                        st.write(f"- 行数: {st.session_state.data.shape[0]}")
                        st.write(f"- 缺失值总数: {st.session_state.data.isnull().sum().sum()}")
                    with col2:
                        st.write("**处理后:**")
                        st.write(f"- 行数: {cleaned_data.shape[0]}")
                        st.write(f"- 缺失值总数: {cleaned_data.isnull().sum().sum()}")
                    
                except Exception as e:
                    st.error(f"数据清洗失败: {str(e)}")
    
    # 使用处理后的数据或原始数据
    current_data = st.session_state.processed_data if 'processed_data' in st.session_state and st.session_state.processed_data is not None else st.session_state.data
    
    # 统计分析部分
    with st.expander("📊 统计分析", expanded=True):
        st.write("### 统计分析")
        
        if st.button("生成统计报告"):
            with st.spinner("正在生成统计分析报告..."):
                try:
                    # 生成描述性统计
                    descriptive_stats = processor.generate_descriptive_stats(current_data)
                    st.session_state.descriptive_stats = descriptive_stats
                    
                    # 计算相关性矩阵（仅数值型列）
                    numeric_cols = current_data.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 1:
                        correlation_matrix = processor.calculate_correlation(current_data)
                        st.session_state.correlation_matrix = correlation_matrix
                    
                    st.success("统计分析完成！")
                except Exception as e:
                    st.error(f"统计分析失败: {str(e)}")
        
        # 显示描述性统计
        if 'descriptive_stats' in st.session_state and st.session_state.descriptive_stats is not None:
            st.write("#### 描述性统计")
            st.dataframe(st.session_state.descriptive_stats.style.format(precision=2))
        
        # 显示相关性矩阵
        if 'correlation_matrix' in st.session_state and st.session_state.correlation_matrix is not None:
            st.write("#### 相关性矩阵")
            st.dataframe(st.session_state.correlation_matrix.style.format(precision=3))
    
    # 特征工程部分
    with st.expander("⚙️ 特征工程", expanded=True):
        st.write("### 特征工程")
        
        # 编码类别特征
        encode_categorical = st.checkbox("编码类别特征", value=False)
        if encode_categorical:
            encode_method = st.radio(
                "选择编码方法",
                options=["标签编码 (Label Encoding)", "独热编码 (One-Hot Encoding)"],
                index=0
            )
        
        # 缩放数值特征
        scale_features = st.checkbox("缩放数值特征", value=False)
        if scale_features:
            scale_method = st.radio(
                "选择缩放方法",
                options=["标准缩放 (Standardization)", "最小-最大缩放 (Min-Max)"],
                index=0
            )
        
        # 应用特征工程
        if st.button("应用特征工程"):
            with st.spinner("正在进行特征工程..."):
                try:
                    # 使用当前数据
                    fe_data = current_data.copy()
                    
                    # 应用类别编码
                    if encode_categorical:
                        method = "label" if encode_method == "标签编码 (Label Encoding)" else "onehot"
                        fe_data = processor.encode_categorical(fe_data, method=method)
                    
                    # 应用特征缩放
                    if scale_features:
                        method = "standard" if scale_method == "标准缩放 (Standardization)" else "minmax"
                        # 只缩放数值列
                        numeric_cols = fe_data.select_dtypes(include=['number']).columns
                        if len(numeric_cols) > 0:
                            fe_data = processor.scale_features(fe_data, columns=numeric_cols, method=method)
                    
                    # 更新会话状态
                    st.session_state.processed_data = fe_data
                    st.success(f"特征工程完成！处理后列数: {fe_data.shape[1]}")
                    
                    # 显示部分处理后的数据
                    st.write("处理后的数据预览:")
                    st.dataframe(fe_data.head())
                    
                except Exception as e:
                    st.error(f"特征工程失败: {str(e)}")
    
    # 导入模型选择器
    from src.model_selection.model_selector import ModelSelector
    
    # 初始化模型选择器
    selector = ModelSelector()
    
    # 分析数据特征
    st.write("### 📊 数据特征分析")
    data_features = selector.analyze_data_features(current_data)
    
    # 显示数据特征
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**样本数量:** {data_features['n_rows']}")
        st.write(f"**特征数量:** {data_features['n_columns']}")
        st.write(f"**数值型特征:** {data_features['n_numeric_columns']}")
        st.write(f"**类别型特征:** {data_features['n_categorical_columns']}")
    with col2:
        st.write(f"**是否有缺失值:** {'是' if data_features['has_missing_values'] else '否'}")
        if data_features['has_missing_values']:
            st.write(f"**缺失值百分比:** {data_features['missing_percentage']:.2f}%")
        st.write(f"**是否有日期列:** {'是' if data_features['has_date_column'] else '否'}")
        if data_features['has_date_column']:
            st.write(f"**日期列:** {', '.join(data_features['date_columns'])}")
    
    # 目标列选择
    st.write("### 🎯 目标列选择")
    numeric_columns = data_features['numeric_columns']
    categorical_columns = data_features['categorical_columns']
    
    # 创建下拉选项
    target_options = ['无（仅进行探索性分析）'] + numeric_columns + categorical_columns
    target_column = st.selectbox(
        "选择目标列（用于预测分析）",
        target_options,
        index=0
    )
    
    # 用户偏好设置
    st.write("### ⚙️ 分析偏好设置")
    
    # 获取支持的模型类型
    model_types = selector.get_supported_model_types()
    model_type_map = {
        'regression': '回归分析（预测连续值）',
        'classification': '分类分析（预测类别）',
        'clustering': '聚类分析（数据分组）',
        'time_series': '时间序列分析（时序预测）',
        'anomaly_detection': '异常检测',
        'descriptive': '描述性统计分析',
        'contrast_analysis': '反差分析（组间差异比较）',
        'reliability_analysis': '信度分析（克朗巴赫α系数）',
        'validity_analysis': '效度分析（结构与效标效度）'
    }
    
    # 创建模型类型选项
    type_options = ['自动选择（推荐）'] + [model_type_map[mt] for mt in model_types] + [model_type_map['contrast_analysis'], model_type_map['reliability_analysis'], model_type_map['validity_analysis']]
    user_pref = st.selectbox(
        "选择分析类型",
        type_options,
        index=0
    )
    
    # 转换用户偏好为内部模型类型
    user_preference = None
    if user_pref != '自动选择（推荐）':
        # 找到对应的模型类型
        for mt, display_name in model_type_map.items():
            if display_name == user_pref:
                user_preference = mt
                break
    
    # 特殊分析类型处理
    special_analysis_types = ['contrast_analysis', 'reliability_analysis', 'validity_analysis']
    is_special_analysis = user_preference in special_analysis_types
    
    # 推荐模型/执行分析
    if st.button("🔍 执行分析", use_container_width=True):
        # 显示加载状态
        with st.spinner("正在分析数据..."):
            # 特殊分析类型处理
            if is_special_analysis:
                # 初始化DataProcessor
                processor = DataProcessor()
                analysis_results = None
                
                try:
                    # 执行对应的特殊分析
                    if user_preference == 'contrast_analysis':
                        # 反差分析需要选择分组列和数值列
                        numeric_cols = current_data.select_dtypes(include=['number']).columns.tolist()
                        categorical_cols = current_data.select_dtypes(include=['object', 'category']).columns.tolist()
                        
                        if not categorical_cols:
                            st.error("反差分析需要至少一个分类列作为分组依据")
                            return
                        if not numeric_cols:
                            st.error("反差分析需要至少一个数值列作为分析对象")
                            return
                        
                        # 存储选择的分析类型
                        st.session_state.analysis_type = 'contrast_analysis'
                        st.session_state.analysis_data = current_data
                        st.success("已选择反差分析，请在下一页面选择分组列和数值列")
                        st.session_state.current_step = 'visualize'
                        st.rerun()
                    
                    elif user_preference == 'reliability_analysis':
                        # 执行信度分析
                        analysis_results = processor.reliability_analysis(current_data)
                        st.session_state.special_analysis_results = analysis_results
                        st.session_state.analysis_type = 'reliability_analysis'
                        st.session_state.current_step = 'visualize'
                        st.rerun()
                    
                    elif user_preference == 'validity_analysis':
                        # 执行效度分析
                        analysis_results = processor.validity_analysis(current_data)
                        st.session_state.special_analysis_results = analysis_results
                        st.session_state.analysis_type = 'validity_analysis'
                        st.session_state.current_step = 'visualize'
                        st.rerun()
                except Exception as e:
                    st.error(f"分析执行失败: {str(e)}")
            else:
                # 处理常规分析类型
                # 处理目标列
                target_col = None if target_column == '无（仅进行探索性分析）' else target_column
                
                # 获取推荐模型
                recommendations = selector.recommend_models(
                    current_data,
                    target_column=target_col,
                    user_preference=user_preference,
                    n_recommendations=3
                )
                
                # 显示推荐结果
                st.session_state.recommendations = recommendations
                
                # 自动选择模式下，直接选择第一个推荐的模型并跳转到可视化页面
                if user_pref == '自动选择（推荐）' and recommendations:
                    st.session_state.selected_model = recommendations[0]
                    st.success(f"已自动选择最佳匹配模型: {recommendations[0].model_name} (匹配度: {recommendations[0].suitability_score:.1f}%)")
                    st.session_state.current_step = 'visualize'
                    st.rerun()
                
                # 显示推荐的模型列表供用户选择
                st.write("### 📋 推荐的分析模型")
                
                for i, rec in enumerate(recommendations, 1):
                    with st.expander(f"{i}. {rec.model_name} (匹配度: {rec.suitability_score:.1f}%)"):
                        st.write(f"**模型类型:** {model_type_map[rec.model_type]}")
                        st.write(f"**描述:** {rec.description}")
                        st.write(f"**推荐理由:** {rec.reason}")
                        
                        # 创建选择按钮
                        if st.button(f"选择此模型", key=f"select_model_{i}"):
                            st.session_state.selected_model = rec
                            st.success(f"已选择模型: {rec.model_name}")
    
    # 如果已经选择了模型，显示下一步按钮
    if hasattr(st.session_state, 'selected_model') and st.session_state.selected_model:
        st.write(f"### ✅ 已选择模型: {st.session_state.selected_model.model_name}")
        
        if st.button("📈 下一步：生成可视化", use_container_width=True):
            st.session_state.current_step = 'visualize'
            st.rerun()
    
    # 上一步按钮
    if st.button("⬅️ 返回数据上传", use_container_width=True):
        st.session_state.current_step = 'upload'
        st.experimental_rerun()


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
    
    # 报告内容选择
    st.subheader("报告内容选择")
    
    # 选择要包含的内容部分
    include_executive_summary = st.checkbox("执行摘要", value=True)
    include_data_overview = st.checkbox("数据概览", value=True)
    include_preprocessing = st.checkbox("数据预处理", value=True)
    include_analysis_results = st.checkbox("分析结果", value=True)
    include_visualizations = st.checkbox("数据可视化", value=True)
    include_conclusion = st.checkbox("结论与建议", value=True)
    
    # 自定义输出路径
    custom_output_path = st.checkbox("自定义输出路径")
    output_path = None
    if custom_output_path:
        default_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = st.text_input("输出路径", value=default_path)
    
    # 生成报告按钮
    if st.button("生成Word报告", use_container_width=True):
        try:
            with st.spinner("正在生成报告..."):
                # 创建高级报告生成器
                report_gen = create_advanced_report_generator()
                
                # 准备分析结果
                analysis_results = st.session_state.analysis_results.copy() if hasattr(st.session_state, 'analysis_results') else {}
                
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
                    output_path=full_output_path
                )
                
                # 保存报告路径到会话状态
                st.session_state.report_path = saved_path
                
                # 更新进度
                st.session_state.progress = 100
                
                st.success(f"报告已成功生成并保存至：{saved_path}")
                
                # 显示打开文件按钮
                if st.button("查看报告", use_container_width=True):
                    # 在Windows上打开文件
                    if os.path.exists(saved_path):
                        os.startfile(saved_path)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            st.error(f"生成报告时出错: {str(e)}")
            
            # 显示详细错误信息的折叠区域
            with st.expander("查看详细错误信息"):
                st.code(error_details)
            
            # 记录到日志
            logging.getLogger(__name__).error(f"报告生成失败: {str(e)}")
            logging.getLogger(__name__).error(f"详细错误: {error_details}")
    
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
    
    # 上一步按钮
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