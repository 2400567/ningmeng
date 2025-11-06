#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI数据分析系统 - 增强版主应用
集成所有6个核心模块，实现智能化的分析工作流
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加模块路径
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# 导入所有模块
try:
    from template_management.template_manager import TemplateManager, create_template_manager, render_template_upload_ui
    from data_processing.variable_merger import VariableMerger, create_variable_merger, render_variable_merger_ui
    from ai_analysis.model_selector import AIAnalysisEngine, create_ai_analysis_engine, render_ai_analysis_ui
    from results_display.spssau_renderer import SPSSAUResultRenderer, create_spssau_renderer, render_spssau_results
    from report_generation.ai_report_generator import AcademicReportGenerator, create_report_generator, render_report_generation_ui
    from literature.smart_literature import LiteratureSearchEngine, ReferenceFormatter, create_literature_system, render_literature_system_ui
    
    # 导入题项变量映射系统
    from item_variable_mapper import ItemVariableMapper, create_item_mapping_interface
    
    logger.info("所有模块导入成功")
except ImportError as e:
    logger.error(f"模块导入失败: {e}")
    st.error(f"模块导入失败: {e}")

# 页面配置
st.set_page_config(
    page_title="AI数据分析系统 - 增强版",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .workflow-step {
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    
    .step-number {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #667eea;
        color: white;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
        font-weight: bold;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    
    .warning-box {
        padding: 1rem;
        border-radius: 10px;
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        border-radius: 10px;
        background: #d6f5f5;
        border: 1px solid #b8e6e6;
        color: #0c5460;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """初始化会话状态"""
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 1
    
    if 'template_uploaded' not in st.session_state:
        st.session_state.template_uploaded = False
    
    if 'data_uploaded' not in st.session_state:
        st.session_state.data_uploaded = False
    
    if 'variables_merged' not in st.session_state:
        st.session_state.variables_merged = False
    
    if 'analysis_completed' not in st.session_state:
        st.session_state.analysis_completed = False
    
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    
    # 初始化组件
    if 'template_manager' not in st.session_state:
        st.session_state.template_manager = create_template_manager()
    
    if 'variable_merger' not in st.session_state:
        st.session_state.variable_merger = create_variable_merger()
    
    if 'ai_analysis_engine' not in st.session_state:
        st.session_state.ai_analysis_engine = create_ai_analysis_engine()
    
    if 'spssau_renderer' not in st.session_state:
        st.session_state.spssau_renderer = create_spssau_renderer()
    
    if 'report_generator' not in st.session_state:
        st.session_state.report_generator = create_report_generator()
    
    if 'literature_engine' not in st.session_state:
        st.session_state.literature_engine, st.session_state.reference_formatter = create_literature_system()

def render_workflow_progress():
    """渲染工作流进度"""
    st.markdown("### 📋 分析工作流进度")
    
    steps = [
        {"name": "模板上传", "completed": st.session_state.template_uploaded, "icon": "📄"},
        {"name": "数据上传", "completed": st.session_state.data_uploaded, "icon": "📊"},
        {"name": "变量合并", "completed": st.session_state.variables_merged, "icon": "🔗"},
        {"name": "AI分析", "completed": st.session_state.analysis_completed, "icon": "🤖"},
        {"name": "结果展示", "completed": st.session_state.analysis_completed, "icon": "📈"},
        {"name": "报告生成", "completed": st.session_state.report_generated, "icon": "📝"}
    ]
    
    cols = st.columns(len(steps))
    
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if step["completed"]:
                st.markdown(f"""
                <div style="text-align: center; color: #28a745;">
                    <div style="font-size: 2rem;">{step['icon']}</div>
                    <div style="font-weight: bold; color: #28a745;">✅ {step['name']}</div>
                </div>
                """, unsafe_allow_html=True)
            elif i + 1 == st.session_state.workflow_step:
                st.markdown(f"""
                <div style="text-align: center; color: #007bff;">
                    <div style="font-size: 2rem;">{step['icon']}</div>
                    <div style="font-weight: bold; color: #007bff;">🔄 {step['name']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; color: #6c757d;">
                    <div style="font-size: 2rem; opacity: 0.5;">{step['icon']}</div>
                    <div style="color: #6c757d;">⏳ {step['name']}</div>
                </div>
                """, unsafe_allow_html=True)

def render_step_1_template_upload():
    """步骤1: 模板上传"""
    st.markdown("""
    <div class="workflow-step">
        <span class="step-number">1</span>
        <strong>📄 模板上传阶段</strong>
        <br><br>
        请首先上传分析模板，系统将根据模板配置后续的数据处理和分析流程。
        <br>
        💡 <em>模板定义了变量结构、分析方法和预期结果格式</em>
    </div>
    """, unsafe_allow_html=True)
    
    # 模板上传界面
    try:
        uploaded_template = render_template_upload_ui(st.session_state.template_manager)
        
        # 额外的调试信息
        if uploaded_template is not None:
            st.info("🔍 **模板上传调试信息**:")
            st.write(f"- 返回值类型: `{type(uploaded_template)}`")
            st.write(f"- 返回值内容: `{repr(uploaded_template)}`")
            st.write(f"- 是否为字符串: `{isinstance(uploaded_template, str)}`")
            st.write(f"- 是否有name属性: `{hasattr(uploaded_template, 'name')}`")
            
            if hasattr(uploaded_template, '__dict__'):
                st.write(f"- 对象属性: `{list(uploaded_template.__dict__.keys())}`")
        
    except Exception as e:
        st.error("🚨 **模板上传过程中发生错误**")
        st.error(f"**错误类型**: {type(e).__name__}")
        st.error(f"**错误信息**: {str(e)}")
        
        # 显示详细的错误信息
        with st.expander("🔍 详细错误信息", expanded=True):
            import traceback
            error_traceback = traceback.format_exc()
            st.code(error_traceback)
            
            # 显示调用栈中的关键信息
            st.write("**错误发生位置分析**:")
            lines = error_traceback.split('\n')
            for i, line in enumerate(lines):
                if 'enhanced_app.py' in line or 'template_manager.py' in line:
                    st.write(f"- {line.strip()}")
        
        st.info("💡 **可能的解决方案**:")
        st.markdown("""
        - 检查上传的文件格式是否正确
        - 确保文件内容符合模板格式要求
        - 尝试重新上传文件
        - 清除浏览器缓存并刷新页面
        - 如果问题持续，请联系技术支持
        """)
        return
    
    if uploaded_template:
        # 额外的调试信息
        st.info("🔍 **模板上传调试信息**:")
        st.write(f"- 返回值类型: `{type(uploaded_template)}`")
        st.write(f"- 返回值内容: `{repr(uploaded_template)}`")
        st.write(f"- 是否为字符串: `{isinstance(uploaded_template, str)}`")
        st.write(f"- 是否有name属性: `{hasattr(uploaded_template, 'name')}`")
        
        if hasattr(uploaded_template, '__dict__'):
            st.write(f"- 对象属性: `{list(uploaded_template.__dict__.keys())}`")
        
        # 特殊处理：如果返回的是字符串，尝试获取对象
        if isinstance(uploaded_template, str):
            st.warning(f"⚠️ 检测到返回值是字符串: {uploaded_template}")
            st.info("🔄 尝试从模板管理器获取对象...")
            try:
                template_obj = st.session_state.template_manager.get_template(uploaded_template)
                if template_obj:
                    st.success("✅ 成功获取模板对象")
                    uploaded_template = template_obj
                    # 清除冲突的状态
                    if 'selected_template' in st.session_state:
                        del st.session_state['selected_template']
                else:
                    st.error("❌ 无法找到对应的模板对象")
                    return
            except Exception as e:
                st.error(f"❌ 获取模板对象失败: {e}")
                return
        
        # 验证模板对象类型
        if not hasattr(uploaded_template, 'name'):
            st.error("🚨 **模板对象类型错误**")
            st.error(f"**实际类型**: {type(uploaded_template)}")
            st.error(f"**期望类型**: AnalysisTemplate")
            
            with st.expander("🔍 错误详情", expanded=False):
                st.write("**实际返回值**:")
                st.code(str(uploaded_template))
            return
        st.session_state.template_uploaded = True
        st.session_state.workflow_step = 2
        st.session_state.current_template = uploaded_template
        
        st.markdown("""
        <div class="success-box">
            ✅ <strong>模板上传成功！</strong><br>
            系统已解析模板配置，可以继续下一步数据上传。
        </div>
        """, unsafe_allow_html=True)
        
        # 显示模板摘要
        with st.expander("📋 模板详情"):
            # 安全访问名称，兼容字符串/对象
            safe_name = getattr(uploaded_template, 'name', str(uploaded_template))
            st.write(f"**模板名称**: {safe_name}")
            st.write(f"**分析类型**: {uploaded_template.template_type}")
            st.write(f"**变量数量**: {len(uploaded_template.variables)}")
            
            # 检查是否有合并规则属性
            if hasattr(uploaded_template, 'merge_rules') and uploaded_template.merge_rules:
                st.write(f"**合并规则**: {len(uploaded_template.merge_rules)} 条")
        
        if st.button("🚀 继续下一步", type="primary"):
            st.rerun()

def render_step_2_data_upload():
    """步骤2: 数据上传"""
    if not st.session_state.template_uploaded:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>请先完成模板上传</strong><br>
            数据上传需要基于已上传的模板进行验证和处理。
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("""
    <div class="workflow-step">
        <span class="step-number">2</span>
        <strong>📊 数据上传阶段</strong>
        <br><br>
        现在可以上传您的调查数据，系统将根据模板验证数据格式。
        <br>
        💡 <em>支持CSV、Excel等格式，请确保数据列名与模板匹配</em>
    </div>
    """, unsafe_allow_html=True)
    
    # 数据上传
    uploaded_file = st.file_uploader(
        "选择数据文件",
        type=['csv', 'xlsx', 'xls'],
        help="请上传包含调查数据的文件"
    )
    
    if uploaded_file is not None:
        try:
            # 读取数据
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # 数据验证
            template = st.session_state.current_template
            missing_cols = []
            
            # 调试信息
            st.info("🔍 **数据验证调试信息**:")
            st.write(f"- 模板类型: `{type(template)}`")
            st.write(f"- variables类型: `{type(template.variables)}`")
            st.write(f"- variables内容: `{template.variables}`")
            if template.variables:
                st.write(f"- 第一个变量类型: `{type(template.variables[0])}`")
            
            # 修复：variables是字符串列表，不是对象列表
            for var in template.variables:
                # var 本身就是字符串，不需要 .name
                if isinstance(var, str):
                    var_name = var
                else:
                    # 如果是对象，才使用 .name
                    var_name = var.name if hasattr(var, 'name') else str(var)
                
                if var_name not in df.columns:
                    missing_cols.append(var_name)
            
            if missing_cols:
                st.error(f"数据中缺少以下必需变量: {', '.join(missing_cols)}")
                st.write("**可用列名:**", list(df.columns))
                
                # 添加智能变量映射功能
                st.markdown("---")
                st.subheader("🧠 智能变量映射")
                st.info("系统检测到变量名不匹配，为您提供智能映射建议：")
                
                # 导入映射系统
                import sys
                import os
                sys.path.append(os.getcwd())
                from variable_mapping_system import create_variable_mapping_suggestions
                
                # 创建映射建议
                mapping_suggestions = create_variable_mapping_suggestions(missing_cols, df.columns)
                
                # 显示映射界面
                st.write("**📋 变量映射建议:**")
                variable_mapping = {}
                
                for template_var in missing_cols:
                    suggestions = mapping_suggestions.get(template_var, [])
                    
                    st.write(f"**模板变量**: `{template_var}`")
                    
                    if suggestions:
                        # 显示建议的映射
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.write("**建议映射:**")
                        with col2:
                            # 创建选择框
                            options = ["不映射"] + suggestions
                            selected = st.selectbox(
                                f"选择 {template_var} 的映射",
                                options,
                                key=f"mapping_{template_var}",
                                help=f"选择数据中哪一列对应模板变量 {template_var}"
                            )
                            if selected != "不映射":
                                variable_mapping[template_var] = selected
                    else:
                        st.write("❌ 未找到合适的映射建议")
                        # 手动选择
                        manual_selection = st.selectbox(
                            f"手动选择 {template_var} 的映射",
                            ["不映射"] + list(df.columns),
                            key=f"manual_{template_var}"
                        )
                        if manual_selection != "不映射":
                            variable_mapping[template_var] = manual_selection
                    
                    st.write("---")
                
                # 应用映射按钮
                if st.button("🔄 应用变量映射", type="primary"):
                    if variable_mapping:
                        # 创建映射后的数据副本
                        mapped_df = df.copy()
                        
                        # 重命名列
                        rename_dict = {v: k for k, v in variable_mapping.items()}
                        mapped_df = mapped_df.rename(columns=rename_dict)
                        
                        # 验证映射后的结果
                        remaining_missing = []
                        for var in template.variables:
                            if isinstance(var, str):
                                var_name = var
                            else:
                                var_name = var.name if hasattr(var, 'name') else str(var)
                            
                            if var_name not in mapped_df.columns:
                                remaining_missing.append(var_name)
                        
                        if remaining_missing:
                            st.warning(f"映射后仍缺少变量: {', '.join(remaining_missing)}")
                        else:
                            # 映射成功
                            st.session_state.uploaded_data = mapped_df
                            st.session_state.variable_mapping = variable_mapping
                            st.session_state.data_uploaded = True
                            st.session_state.workflow_step = 3
                            
                            st.success("✅ 变量映射成功！数据已准备就绪。")
                            
                            # 显示映射摘要
                            with st.expander("📊 映射摘要"):
                                st.write("**应用的映射关系:**")
                                for template_var, data_col in variable_mapping.items():
                                    st.write(f"- `{template_var}` ← `{data_col}`")
                            
                            st.rerun()
                    else:
                        st.warning("请至少选择一个变量映射")
            else:
                st.session_state.uploaded_data = df
                st.session_state.data_uploaded = True
                st.session_state.workflow_step = 3
                
                st.markdown("""
                <div class="success-box">
                    ✅ <strong>数据上传成功！</strong><br>
                    数据格式验证通过，可以进行变量合并处理。
                </div>
                """, unsafe_allow_html=True)
                
                # 显示数据摘要
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("样本数量", len(df))
                with col2:
                    st.metric("变量数量", len(df.columns))
                with col3:
                    st.metric("缺失值", df.isnull().sum().sum())
                
                # 数据预览
                with st.expander("📊 数据预览"):
                    st.dataframe(df.head(10))
                
                # 添加题项变量映射选项
                st.markdown("---")
                st.subheader("🎯 题项变量映射（可选）")
                st.info("""
                如果您的数据包含问卷题项（如Q1, Q2等），可以使用题项变量映射功能
                将题项按照构念分组，便于后续进行信度分析和结构方程建模。
                """)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("� 启用题项变量映射", key="enable_item_mapping"):
                        st.session_state.show_item_mapping = True
                        st.rerun()
                
                with col2:
                    if st.button("⏭️ 跳过，继续下一步", type="primary"):
                        st.rerun()
                
                # 题项变量映射界面
                if st.session_state.get('show_item_mapping', False):
                    st.markdown("---")
                    try:
                        # 创建题项映射系统
                        mapper = ItemVariableMapper()
                        
                        # 检查数据中是否包含题项格式的列
                        question_cols = [col for col in df.columns if any(pattern in col.upper() for pattern in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])]
                        
                        if question_cols:
                            st.success(f"✅ 检测到 {len(question_cols)} 个可能的题项列")
                            
                            # 渲染题项映射界面
                            mapping = mapper.render_mapping_interface(list(df.columns))
                            
                            if mapping and st.button("✅ 应用题项映射并继续", type="primary"):
                                # 应用映射
                                mapped_df = mapper.apply_variable_mapping(df, mapping)
                                st.session_state.uploaded_data = mapped_df
                                st.session_state.item_mapping_applied = True
                                st.success("✅ 题项变量映射已应用")
                                st.rerun()
                        else:
                            st.warning("⚠️ 未检测到标准题项格式（Q1, Q2等），您可以跳过此步骤")
                            if st.button("确认跳过题项映射"):
                                st.session_state.show_item_mapping = False
                                st.rerun()
                    
                    except Exception as e:
                        st.error(f"题项映射功能出错: {e}")
                        if st.button("跳过题项映射，继续"):
                            st.session_state.show_item_mapping = False
                            st.rerun()
        
        except Exception as e:
            st.error("🚨 **数据读取失败**")
            st.error(f"**错误信息**: {str(e)}")
            st.error(f"**错误类型**: {type(e).__name__}")
            
            # 显示详细的错误信息
            with st.expander("🔍 详细错误信息", expanded=True):
                import traceback
                error_traceback = traceback.format_exc()
                st.code(error_traceback)
                
                # 显示相关状态信息
                st.write("**相关状态信息**:")
                template = st.session_state.get('current_template')
                if template:
                    st.write(f"- 模板类型: {type(template)}")
                    st.write(f"- 模板名称: {getattr(template, 'name', 'N/A')}")
                    st.write(f"- 变量类型: {type(getattr(template, 'variables', None))}")
                    st.write(f"- 变量内容: {getattr(template, 'variables', 'N/A')}")
                else:
                    st.write("- 当前模板: 未找到")
            
            st.info("💡 **可能的解决方案**:")
            st.markdown("""
            1. **检查数据文件格式**: 确保是有效的CSV或Excel文件
            2. **检查文件编码**: 尝试使用UTF-8编码保存文件
            3. **检查数据内容**: 确保文件包含有效的数据行和列
            4. **重新上传模板**: 使用调试工具重置状态后重新上传
            5. **检查文件大小**: 确保文件不超过200MB限制
            """)
            
            # 提供快速修复按钮
            if st.button("🔄 重置当前步骤"):
                if 'uploaded_data' in st.session_state:
                    del st.session_state['uploaded_data']
                st.session_state.data_uploaded = False
                st.session_state.workflow_step = 2
                st.rerun()

def render_step_3_variable_merging():
    """步骤3: 变量合并"""
    if not st.session_state.data_uploaded:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>请先完成数据上传</strong><br>
            变量合并需要基于已上传的数据进行。
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("""
    <div class="workflow-step">
        <span class="step-number">3</span>
        <strong>🔗 变量合并阶段</strong>
        <br><br>
        根据模板配置对相关变量进行合并处理，生成分析所需的复合变量。
        <br>
        💡 <em>支持均值、求和、加权平均、因子得分等多种合并方法</em>
    </div>
    """, unsafe_allow_html=True)
    
    # 变量合并界面
    merger = st.session_state.variable_merger
    template = st.session_state.current_template
    data = st.session_state.uploaded_data
    
    # 应用模板中的合并规则
    if hasattr(template, 'merge_rules') and template.merge_rules and not st.session_state.variables_merged:
        st.write("**📋 模板预定义的合并规则:**")
        
        for rule in template.merge_rules:
            with st.expander(f"🔗 {rule.target_variable}"):
                st.write(f"**目标变量**: {rule.target_variable}")
                st.write(f"**源变量**: {', '.join(rule.source_variables)}")
                st.write(f"**合并方法**: {rule.method}")
                
                if st.button(f"应用规则: {rule.target_variable}", key=f"apply_{rule.target_variable}"):
                    try:
                        merged_data = merger.apply_merge_rule(data, rule)
                        st.session_state.merged_data = merged_data
                        st.success(f"变量 {rule.target_variable} 合并成功！")
                    except Exception as e:
                        st.error(f"合并失败: {e}")
        
        if st.button("🔄 应用所有合并规则", type="primary"):
            try:
                merged_data = data.copy()
                if hasattr(template, 'merge_rules') and template.merge_rules:
                    for rule in template.merge_rules:
                        merged_data = merger.apply_merge_rule(merged_data, rule)
                
                st.session_state.merged_data = merged_data
                st.session_state.variables_merged = True
                st.session_state.workflow_step = 4
                
                st.markdown("""
                <div class="success-box">
                    ✅ <strong>变量合并完成！</strong><br>
                    所有预定义合并规则已应用，可以进行AI分析。
                </div>
                """, unsafe_allow_html=True)
                
                st.rerun()
            except Exception as e:
                st.error(f"批量合并失败: {e}")
    
    # 手动合并选项
    st.markdown("---")
    st.write("**🛠️ 手动变量合并:**")
    merged_data = render_variable_merger_ui(merger, data)
    
    if merged_data is not None:
        st.session_state.merged_data = merged_data
        st.session_state.variables_merged = True
        st.session_state.workflow_step = 4
        
        if st.button("🚀 继续AI分析", type="primary"):
            st.rerun()

def render_step_4_ai_analysis():
    """步骤4: AI分析"""
    if not st.session_state.variables_merged:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>请先完成变量合并</strong><br>
            AI分析需要基于合并后的数据进行。
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("""
    <div class="workflow-step">
        <span class="step-number">4</span>
        <strong>🤖 AI分析阶段</strong>
        <br><br>
        使用AI分析引擎对数据进行深度分析，支持多种统计模型和机器学习方法。
        <br>
        💡 <em>基于模板自动选择最适合的分析方法，AI解读分析结果</em>
    </div>
    """, unsafe_allow_html=True)
    
    # AI分析界面
    engine = st.session_state.ai_analysis_engine
    template = st.session_state.current_template
    data = st.session_state.merged_data
    
    # 根据模板自动选择分析方法
    st.write(f"**🎯 推荐分析方法**: {template.template_type}")
    
    analysis_results = render_ai_analysis_ui(engine, data, template.template_type)
    
    if analysis_results:
        st.session_state.analysis_results = analysis_results
        st.session_state.analysis_completed = True
        st.session_state.workflow_step = 5
        
        st.markdown("""
        <div class="success-box">
            ✅ <strong>AI分析完成！</strong><br>
            分析结果已生成，可以查看SPSSAU风格的专业展示。
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 查看分析结果", type="primary"):
            st.rerun()

def render_step_5_results_display():
    """步骤5: 结果展示"""
    if not st.session_state.analysis_completed:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>请先完成AI分析</strong><br>
            结果展示需要基于分析结果进行。
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("""
    <div class="workflow-step">
        <span class="step-number">5</span>
        <strong>📈 专业结果展示</strong>
        <br><br>
        使用SPSSAU风格的专业界面展示分析结果，包括统计表格、可视化图表和AI解读。
        <br>
        💡 <em>专业的学术级别输出，可直接用于论文写作</em>
    </div>
    """, unsafe_allow_html=True)
    
    # 结果展示
    renderer = st.session_state.spssau_renderer
    results = st.session_state.analysis_results
    
    render_spssau_results(renderer, results)
    
    # 文献系统
    st.markdown("---")
    st.markdown("### 📚 参考文献管理")
    
    literature_engine = st.session_state.literature_engine
    reference_formatter = st.session_state.reference_formatter
    
    selected_references = render_literature_system_ui(literature_engine, reference_formatter)
    
    if selected_references:
        st.session_state.selected_references = selected_references
    
    # 继续生成报告
    if st.button("📝 生成学术报告", type="primary"):
        st.session_state.workflow_step = 6
        st.rerun()

def render_step_6_report_generation():
    """步骤6: 报告生成"""
    if not st.session_state.analysis_completed:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>请先完成分析</strong><br>
            报告生成需要基于分析结果进行。
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("""
    <div class="workflow-step">
        <span class="step-number">6</span>
        <strong>📝 AI学术报告生成</strong>
        <br><br>
        基于分析结果和参考文献，AI自动生成符合学术标准的研究报告。
        <br>
        💡 <em>包含摘要、方法、结果、讨论等完整章节，支持Word导出</em>
    </div>
    """, unsafe_allow_html=True)
    
    # 报告生成界面
    generator = st.session_state.report_generator
    results = st.session_state.analysis_results
    references = st.session_state.get('selected_references', [])
    
    report_content = render_report_generation_ui(generator, results, references)
    
    if report_content:
        st.session_state.report_generated = True
        
        st.markdown("""
        <div class="success-box">
            ✅ <strong>学术报告生成完成！</strong><br>
            完整的分析工作流已完成，您的AI数据分析报告已准备就绪。
        </div>
        """, unsafe_allow_html=True)

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("## 🎛️ 控制面板")
        
        # 工作流控制
        st.markdown("### 📋 工作流控制")
        
        step_options = [
            "1️⃣ 模板上传",
            "2️⃣ 数据上传", 
            "3️⃣ 变量合并",
            "4️⃣ AI分析",
            "5️⃣ 结果展示",
            "6️⃣ 报告生成"
        ]
        
        selected_step = st.selectbox(
            "跳转到步骤",
            step_options,
            index=st.session_state.workflow_step - 1
        )
        
        new_step = step_options.index(selected_step) + 1
        if new_step != st.session_state.workflow_step:
            st.session_state.workflow_step = new_step
            st.rerun()
        
        st.markdown("---")
        
        # 系统状态
        st.markdown("### 📊 系统状态")
        
        status_items = [
            ("模板", st.session_state.template_uploaded),
            ("数据", st.session_state.data_uploaded),
            ("合并", st.session_state.variables_merged),
            ("分析", st.session_state.analysis_completed),
            ("报告", st.session_state.report_generated)
        ]
        
        for name, status in status_items:
            icon = "✅" if status else "❌"
            st.write(f"{icon} {name}")
        
        st.markdown("---")
        
        # 重置选项
        st.markdown("### 🔄 系统控制")
        
        if st.button("🔄 重置工作流"):
            for key in list(st.session_state.keys()):
                if key not in ['template_manager', 'variable_merger', 'ai_analysis_engine', 
                             'spssau_renderer', 'report_generator', 'literature_engine', 
                             'reference_formatter']:
                    del st.session_state[key]
            
            initialize_session_state()
            st.rerun()
        
        if st.button("💾 保存会话"):
            st.success("会话状态已保存")
        
        st.markdown("---")
        
        # 帮助信息
        with st.expander("❓ 使用帮助"):
            st.markdown("""
            **工作流说明:**
            1. 📄 上传分析模板
            2. 📊 上传调查数据  
            3. 🔗 进行变量合并
            4. 🤖 执行AI分析
            5. 📈 查看专业结果
            6. 📝 生成学术报告
            
            **注意事项:**
            - 必须按顺序完成各步骤
            - 模板定义了分析流程
            - 数据格式需与模板匹配
            """)

def main():
    """主函数"""
    # 添加调试和重置功能到侧边栏
    with st.sidebar:
        st.markdown("### 🔧 调试工具")
        if st.button("🔄 重置所有状态", help="清除所有session state，解决状态冲突"):
            # 清除所有session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ 状态已重置")
            st.rerun()
        
        if st.button("🧹 清除模板选择", help="清除当前模板选择状态"):
            if 'selected_template' in st.session_state:
                del st.session_state['selected_template']
            if 'current_template' in st.session_state:
                del st.session_state['current_template']
            st.success("✅ 模板选择已清除")
            st.rerun()
        
        # 显示当前状态信息
        with st.expander("🔍 当前状态信息"):
            st.write("**Session State Keys:**")
            for key in st.session_state.keys():
                value = st.session_state[key]
                if hasattr(value, '__class__'):
                    st.write(f"- {key}: {type(value).__name__}")
                else:
                    st.write(f"- {key}: {type(value)}")
    
    # 初始化
    initialize_session_state()
    
    # 主标题
    st.markdown('<h1 class="main-header">🤖 AI数据分析系统 - 增强版</h1>', unsafe_allow_html=True)
    
    # 系统介绍
    st.markdown("""
    <div class="info-box">
        🎯 <strong>更加智能化的数据分析平台</strong><br>
        集成模板管理、变量合并、AI分析、专业展示、学术报告和文献管理等6大核心功能，
        为您提供从数据到发表的一站式解决方案。
    </div>
    """, unsafe_allow_html=True)
    
    # 渲染侧边栏
    render_sidebar()
    
    # 工作流进度
    render_workflow_progress()
    
    st.markdown("---")
    
    # 根据当前步骤渲染界面
    current_step = st.session_state.workflow_step
    
    if current_step == 1:
        render_step_1_template_upload()
    elif current_step == 2:
        render_step_2_data_upload()
    elif current_step == 3:
        render_step_3_variable_merging()
    elif current_step == 4:
        render_step_4_ai_analysis()
    elif current_step == 5:
        render_step_5_results_display()
    elif current_step == 6:
        render_step_6_report_generation()
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        🤖 AI数据分析系统 v2.0 - 智能化数据分析与学术报告生成平台<br>
        <small>支持UTAUT2、聚类分析、因子分析等多种研究方法</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # 集成自动错误上报包装
    try:
        from auto_issue_reporter import AutoIssueReporter
        AutoIssueReporter.run_with_capture(main, "MAIN_ENTRY")
    except Exception as e:  # noqa: BLE001
        # 如果上报模块自身异常，回退直接执行
        import traceback
        print("[AutoIssueReporter Fallback]", e)
        print(traceback.format_exc())
        main()