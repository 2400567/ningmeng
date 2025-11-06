#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能模板管理系统
提供分析模板的上传、解析、管理功能
"""

import os
import json
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

# 设置日志
logger = logging.getLogger(__name__)

@dataclass
class AnalysisTemplate:
    """分析模板数据结构"""
    name: str
    description: str
    template_type: str  # 'clustering', 'regression', 'factor_analysis', 'structural_equation'
    variables: List[str]
    analysis_steps: List[Dict]
    output_format: Dict
    created_at: str
    merge_rules: List = None  # 可选的合并规则
    
    def __post_init__(self):
        """初始化后处理"""
        if self.merge_rules is None:
            self.merge_rules = []
    
class TemplateManager:
    """智能模板管理器"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
        self.templates: Dict[str, AnalysisTemplate] = {}
        self.load_templates()
        
    def load_templates(self):
        """加载所有模板"""
        template_files = list(self.template_dir.glob("*.json"))
        for template_file in template_files:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template = AnalysisTemplate(**template_data)
                    self.templates[template.name] = template
            except Exception as e:
                logger.error(f"加载模板失败 {template_file}: {e}")
    
    def save_template(self, template: AnalysisTemplate) -> bool:
        """保存模板"""
        try:
            template_file = self.template_dir / f"{template.name}.json"
            template_dict = {
                'name': template.name,
                'description': template.description,
                'template_type': template.template_type,
                'variables': template.variables,
                'analysis_steps': template.analysis_steps,
                'output_format': template.output_format,
                'created_at': template.created_at
            }
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_dict, f, ensure_ascii=False, indent=2)
            
            self.templates[template.name] = template
            return True
        except Exception as e:
            logger.error(f"保存模板失败: {e}")
            return False
    
    def parse_template_from_file(self, uploaded_file) -> Optional[AnalysisTemplate]:
        """从上传文件解析模板"""
        try:
            if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
                # 解析Excel模板
                return self._parse_excel_template(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                # 解析JSON模板
                return self._parse_json_template(uploaded_file)
            elif uploaded_file.name.endswith('.pdf'):
                # 解析PDF模板
                return self._parse_pdf_template(uploaded_file)
            else:
                st.error("不支持的模板格式，请上传Excel、JSON或PDF文件")
                return None
        except Exception as e:
            logger.error(f"解析模板失败: {e}")
            st.error(f"模板解析失败: {str(e)}")
            return None
    
    def _parse_excel_template(self, uploaded_file) -> Optional[AnalysisTemplate]:
        """解析Excel模板"""
        try:
            # 读取Excel文件的多个工作表
            excel_data = pd.read_excel(uploaded_file, sheet_name=None)
            
            # 解析基本信息
            if 'template_info' in excel_data:
                info_df = excel_data['template_info']
                template_name = info_df.loc[info_df['field'] == 'name', 'value'].iloc[0]
                description = info_df.loc[info_df['field'] == 'description', 'value'].iloc[0]
                template_type = info_df.loc[info_df['field'] == 'type', 'value'].iloc[0]
            else:
                # 如果没有模板信息，使用文件名
                template_name = os.path.splitext(uploaded_file.name)[0]
                description = f"从{uploaded_file.name}导入的模板"
                template_type = "custom"
            
            # 解析变量定义
            variables = []
            if 'variables' in excel_data:
                var_df = excel_data['variables']
                variables = var_df['variable_name'].tolist()
            
            # 解析分析步骤
            analysis_steps = []
            if 'analysis_steps' in excel_data:
                steps_df = excel_data['analysis_steps']
                for _, row in steps_df.iterrows():
                    step = {
                        'step_name': row['step_name'],
                        'method': row['method'],
                        'parameters': json.loads(row.get('parameters', '{}'))
                    }
                    analysis_steps.append(step)
            
            # 解析输出格式
            output_format = {
                'tables': True,
                'charts': True,
                'ai_analysis': True,
                'format': 'spssau_style'
            }
            
            template = AnalysisTemplate(
                name=template_name,
                description=description,
                template_type=template_type,
                variables=variables,
                analysis_steps=analysis_steps,
                output_format=output_format,
                created_at=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return template
            
        except Exception as e:
            logger.error(f"解析Excel模板失败: {e}")
            return None
    
    def _parse_json_template(self, uploaded_file) -> Optional[AnalysisTemplate]:
        """解析JSON模板"""
        try:
            content = uploaded_file.read()
            template_data = json.loads(content)
            return AnalysisTemplate(**template_data)
        except Exception as e:
            logger.error(f"解析JSON模板失败: {e}")
            return None
    
    def _parse_pdf_template(self, uploaded_file) -> Optional[AnalysisTemplate]:
        """解析PDF模板"""
        try:
            # 导入PDF处理库
            import PyPDF2
            import io
            
            # 读取PDF内容
            pdf_content = uploaded_file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            # 提取文本内容
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            # 使用AI解析PDF内容（如果有AI客户端）
            template_data = self._extract_template_from_text(text_content, uploaded_file.name)
            
            if template_data:
                return AnalysisTemplate(**template_data)
            else:
                # 创建一个基础模板
                template_name = os.path.splitext(uploaded_file.name)[0]
                return AnalysisTemplate(
                    name=template_name,
                    description=f"从PDF文件 {uploaded_file.name} 提取的模板",
                    template_type="custom",
                    variables=self._extract_variables_from_text(text_content),
                    analysis_steps=[
                        {
                            "step_name": "数据分析",
                            "method": "descriptive_statistics",
                            "parameters": {}
                        }
                    ],
                    output_format={"format": "standard"},
                    created_at=pd.Timestamp.now().isoformat()
                )
                
        except ImportError:
            st.error("PDF解析需要安装PyPDF2库。请运行: pip install PyPDF2")
            return None
        except Exception as e:
            logger.error(f"解析PDF模板失败: {e}")
            st.error(f"PDF解析失败: {str(e)}")
            return None
    
    def _extract_template_from_text(self, text_content: str, filename: str = "PDF模板") -> Optional[Dict]:
        """从文本内容提取模板信息"""
        try:
            # 这里可以集成AI来解析PDF文本内容
            # 目前使用简单的关键词匹配
            
            # 检测分析类型
            template_type = "custom"
            if "UTAUT" in text_content.upper() or "技术接受" in text_content:
                template_type = "technology_acceptance"
            elif "聚类" in text_content or "cluster" in text_content.lower():
                template_type = "clustering"
            elif "因子分析" in text_content or "factor" in text_content.lower():
                template_type = "factor_analysis"
            elif "回归" in text_content or "regression" in text_content.lower():
                template_type = "regression"
            
            # 提取变量
            variables = self._extract_variables_from_text(text_content)
            
            template_name = os.path.splitext(filename)[0]
            
            return {
                "name": template_name,
                "description": f"从PDF文件 {filename} 自动解析的分析模板",
                "template_type": template_type,
                "variables": variables,
                "analysis_steps": [
                    {
                        "step_name": "描述性统计",
                        "method": "descriptive_statistics",
                        "parameters": {}
                    },
                    {
                        "step_name": "主要分析",
                        "method": template_type,
                        "parameters": {}
                    }
                ],
                "output_format": {"format": "academic_report"},
                "created_at": pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"从文本提取模板失败: {e}")
            return None
    
    def _extract_variables_from_text(self, text_content: str) -> List[str]:
        """从文本中提取变量名"""
        variables = []
        
        # 常见的变量模式
        import re
        
        # 查找类似Q1, Q2, VAR1, X1等的变量名
        var_patterns = [
            r'\b[Qq]\d+\b',  # Q1, Q2, q1, q2
            r'\b[Vv][Aa][Rr]\d+\b',  # VAR1, var1
            r'\b[Xx]\d+\b',  # X1, x1
            r'\b[Yy]\d+\b',  # Y1, y1
            r'\b[A-Z]+\d+\b',  # 任何大写字母+数字
        ]
        
        for pattern in var_patterns:
            matches = re.findall(pattern, text_content)
            variables.extend(matches)
        
        # 查找UTAUT2相关变量
        utaut_vars = [
            "PE", "EE", "SI", "FC", "HM", "PV", "HT", "BI", "UB",
            "Performance_Expectancy", "Effort_Expectancy", "Social_Influence",
            "Facilitating_Conditions", "Hedonic_Motivation", "Price_Value",
            "Habit", "Behavioral_Intention", "Use_Behavior"
        ]
        
        for var in utaut_vars:
            if var in text_content:
                variables.append(var)
        
        # 去重并排序
        variables = list(set(variables))
        variables.sort()
        
        # 如果没有找到变量，提供默认变量
        if not variables:
            variables = ["Variable_1", "Variable_2", "Variable_3", "Variable_4", "Variable_5"]
        
        return variables[:20]  # 限制最多20个变量
    
    def get_available_templates(self) -> List[str]:
        """获取可用模板列表"""
        return list(self.templates.keys())
    
    def get_template(self, template_name: str) -> Optional[AnalysisTemplate]:
        """获取指定模板"""
        return self.templates.get(template_name)
    
    def delete_template(self, template_name: str) -> bool:
        """删除模板"""
        try:
            if template_name in self.templates:
                template_file = self.template_dir / f"{template_name}.json"
                if template_file.exists():
                    template_file.unlink()
                del self.templates[template_name]
                return True
            return False
        except Exception as e:
            logger.error(f"删除模板失败: {e}")
            return False

# 预定义模板
PREDEFINED_TEMPLATES = {
    "UTAUT2模型": {
        "name": "UTAUT2模型",
        "description": "统一技术接受与使用理论2.0模型分析",
        "template_type": "structural_equation",
        "variables": [
            "performance_expectancy", "effort_expectancy", "social_influence",
            "facilitating_conditions", "hedonic_motivation", "price_value",
            "habit", "behavioral_intention", "use_behavior"
        ],
        "analysis_steps": [
            {
                "step_name": "描述性统计",
                "method": "descriptive_stats",
                "parameters": {"include_all": True}
            },
            {
                "step_name": "信度分析",
                "method": "reliability_analysis",
                "parameters": {"alpha_threshold": 0.7}
            },
            {
                "step_name": "效度分析",
                "method": "validity_analysis",
                "parameters": {"kmo_threshold": 0.7}
            },
            {
                "step_name": "结构方程建模",
                "method": "structural_equation_modeling",
                "parameters": {"estimation": "ML", "bootstrap": 1000}
            }
        ],
        "output_format": {
            "tables": True,
            "charts": True,
            "ai_analysis": True,
            "format": "spssau_style"
        },
        "created_at": "2025-11-06 12:00:00"
    },
    
    "聚类分析模板": {
        "name": "聚类分析模板",
        "description": "K-means聚类分析专用模板",
        "template_type": "clustering",
        "variables": ["cluster_variables"],
        "analysis_steps": [
            {
                "step_name": "数据预处理",
                "method": "data_preprocessing",
                "parameters": {"standardize": True, "handle_missing": "drop"}
            },
            {
                "step_name": "K-means聚类",
                "method": "kmeans_clustering",
                "parameters": {"n_clusters": 4, "random_state": 42}
            },
            {
                "step_name": "聚类评估",
                "method": "cluster_evaluation",
                "parameters": {"metrics": ["silhouette", "sse"]}
            },
            {
                "step_name": "方差分析",
                "method": "anova_analysis",
                "parameters": {"post_hoc": "tukey"}
            }
        ],
        "output_format": {
            "tables": True,
            "charts": True,
            "ai_analysis": True,
            "format": "spssau_style"
        },
        "created_at": "2025-11-06 12:00:00"
    }
}

def create_template_manager() -> TemplateManager:
    """创建模板管理器实例"""
    manager = TemplateManager()
    
    # 添加预定义模板
    for template_data in PREDEFINED_TEMPLATES.values():
        template = AnalysisTemplate(**template_data)
        manager.save_template(template)
    
    return manager

def render_template_upload_ui(template_manager: TemplateManager):
    """渲染模板上传界面"""
    st.header("📋 分析模板管理")
    
    # 添加使用说明
    with st.expander("📋 模板文件格式说明", expanded=False):
        st.markdown("""
        **支持的文件格式：**
        
        1. **📊 Excel文件 (.xlsx, .xls)**
           - 包含模板信息、变量定义、分析步骤等工作表
           - 结构化数据，便于精确解析
        
        2. **📄 JSON文件 (.json)**
           - 标准化的模板配置文件
           - 适合程序化生成和交换
        
        3. **📑 PDF文件 (.pdf) - 新功能！**
           - 自动识别研究方法和变量
           - 智能提取UTAUT2、聚类分析等模型
           - 适合从学术论文、研究报告中快速创建模板
        
        **PDF智能解析功能：**
        - 🔍 自动识别分析类型（UTAUT2、聚类分析、因子分析等）
        - 📝 提取变量名（Q1-Q50、PE、EE、SI等）
        - 🧠 基于内容生成分析步骤
        - 📊 创建标准化模板结构
        """)
    
    # 模板上传区域
    st.subheader("📤 上传新模板")
    uploaded_file = st.file_uploader(
        "选择模板文件",
        type=['xlsx', 'xls', 'json', 'pdf'],
        help="支持Excel、JSON或PDF格式的分析模板"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        file_type = uploaded_file.name.split('.')[-1].upper()
        st.info(f"📁 已选择 {file_type} 文件: {uploaded_file.name}")
        
        # 如果是PDF文件，显示特殊提示
        if uploaded_file.name.endswith('.pdf'):
            st.warning("""
            🤖 **PDF智能解析模式**
            
            系统将自动解析PDF内容，提取以下信息：
            - 📊 分析方法类型
            - 📝 变量名和构念
            - 🔗 分析步骤
            
            解析可能需要几秒钟时间...
            """)
        
        # 解析模板
        with st.spinner("正在解析模板文件..."):
            try:
                template = template_manager.parse_template_from_file(uploaded_file)
            except Exception as e:
                st.error(f"模板解析失败: {str(e)}")
                template = None
        
        if template:
            # 根据文件类型显示不同的成功信息
            if uploaded_file.name.endswith('.pdf'):
                st.success(f"🎉 PDF模板 '{template.name}' 智能解析成功！")
                st.info("💡 PDF解析结果仅供参考，建议检查并完善模板配置")
            else:
                st.success(f"✅ 模板 '{template.name}' 解析成功！")
            
            # 显示模板信息
            with st.expander("📋 模板详细信息", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**模板名称**: {template.name}")
                    st.write(f"**模板类型**: {template.template_type}")
                    st.write(f"**创建时间**: {template.created_at}")
                
                with col2:
                    st.write(f"**描述**: {template.description}")
                    st.write(f"**变量数量**: {len(template.variables)}")
                    st.write(f"**分析步骤**: {len(template.analysis_steps)}")
                
                # 显示变量列表
                if template.variables:
                    st.write("**📝 变量列表**:")
                    # 分批显示变量，每行10个
                    for i in range(0, len(template.variables), 10):
                        variables_chunk = template.variables[i:i+10]
                        st.write("  " + ", ".join(variables_chunk))
                
                # 显示分析步骤
                st.write("**🔄 分析步骤**:")
                for i, step in enumerate(template.analysis_steps, 1):
                    st.write(f"  {i}. {step['step_name']} ({step['method']})")
            
            # 如果是PDF解析的模板，提供编辑选项
            if uploaded_file.name.endswith('.pdf'):
                with st.expander("✏️ 编辑和完善模板", expanded=False):
                    st.markdown("**PDF解析可能不够准确，您可以手动完善：**")
                    
                    # 编辑模板名称
                    new_name = st.text_input("模板名称", value=template.name)
                    
                    # 编辑描述
                    new_description = st.text_area("模板描述", value=template.description)
                    
                    # 编辑分析类型
                    analysis_types = [
                        "technology_acceptance", "clustering", "factor_analysis", 
                        "regression", "structural_equation", "custom"
                    ]
                    new_type = st.selectbox(
                        "分析类型", 
                        analysis_types, 
                        index=analysis_types.index(template.template_type) if template.template_type in analysis_types else 0
                    )
                    
                    # 编辑变量
                    variables_text = st.text_area(
                        "变量列表（每行一个）",
                        value="\n".join(template.variables),
                        height=150
                    )
                    
                    if st.button("🔄 更新模板"):
                        # 更新模板信息
                        template.name = new_name
                        template.description = new_description
                        template.template_type = new_type
                        template.variables = [v.strip() for v in variables_text.split('\n') if v.strip()]
                        
                        st.success("模板信息已更新！")
                        st.rerun()
            
            # 保存模板
            if st.button("保存模板", type="primary"):
                if template_manager.save_template(template):
                    st.success("模板保存成功！")
                    # 设置当前模板为刚保存的模板
                    st.session_state.selected_template = template.name
                    st.rerun()
                else:
                    st.error("模板保存失败！")
            
            # 直接返回当前解析的模板对象
            # 清除之前选中的模板，避免冲突
            st.session_state.selected_template = None
            return template
        else:
            # 模板解析失败的情况
            st.error("模板解析失败，请检查文件格式是否正确")
            return None
    
    # 现有模板管理
    st.subheader("现有模板")
    available_templates = template_manager.get_available_templates()
    
    if available_templates:
        for template_name in available_templates:
            template = template_manager.get_template(template_name)
            
            with st.expander(f"📋 {template_name}"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**描述**: {template.description}")
                    st.write(f"**类型**: {template.template_type}")
                    st.write(f"**变量数**: {len(template.variables)}")
                
                with col2:
                    if st.button("选择", key=f"select_{template_name}"):
                        st.session_state.selected_template = template_name
                        st.success(f"已选择模板: {template_name}")
                
                with col3:
                    if st.button("删除", key=f"delete_{template_name}"):
                        if template_manager.delete_template(template_name):
                            st.success("模板删除成功！")
                            st.rerun()
                        else:
                            st.error("模板删除失败！")
    else:
        st.info("暂无模板，请先上传分析模板")
    
    # 返回选中的模板对象，而不是名称
    selected_template_name = st.session_state.get('selected_template')
    if selected_template_name:
        # 清除字符串状态，避免冲突
        st.session_state.selected_template = None
        return template_manager.get_template(selected_template_name)
    return None