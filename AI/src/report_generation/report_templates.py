"""
标准报告模板模块
提供学术论文、商业报告等多种标准模板
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List

class ReportTemplateManager:
    """报告模板管理器"""
    
    def __init__(self):
        self.templates = {
            "academic_paper": self._academic_paper_template(),
            "business_report": self._business_report_template(),
            "journal_article": self._journal_article_template(),
            "research_proposal": self._research_proposal_template(),
            "technical_report": self._technical_report_template(),
            "executive_summary": self._executive_summary_template()
        }
    
    def get_template(self, template_type: str) -> Dict[str, Any]:
        """获取指定类型的报告模板"""
        return self.templates.get(template_type, self._default_template())
    
    def list_available_templates(self) -> List[str]:
        """获取所有可用模板列表"""
        return list(self.templates.keys())
    
    def _academic_paper_template(self) -> Dict[str, Any]:
        """学术论文模板"""
        return {
            "type": "academic_paper",
            "structure": [
                "title",
                "abstract", 
                "keywords",
                "introduction",
                "literature_review",
                "methodology",
                "results",
                "discussion",
                "conclusion",
                "limitations",
                "future_research",
                "references",
                "appendices"
            ],
            "sections": {
                "title": {
                    "format": "# {title}",
                    "guidelines": "简洁明了，准确反映研究内容，15-20字为宜",
                    "example": "基于机器学习的数据分析方法研究"
                },
                "abstract": {
                    "format": "## 摘要\n\n{content}",
                    "guidelines": "200-300字，包含研究背景、方法、主要发现和结论",
                    "structure": ["背景", "目的", "方法", "结果", "结论"],
                    "word_limit": 300
                },
                "keywords": {
                    "format": "**关键词：** {keywords}",
                    "guidelines": "3-5个关键词，反映研究的核心概念",
                    "count_limit": 5
                },
                "introduction": {
                    "format": "## 引言\n\n{content}",
                    "guidelines": "介绍研究背景、问题陈述、研究目标和意义",
                    "structure": ["研究背景", "问题陈述", "研究目标", "研究意义", "论文结构"]
                },
                "literature_review": {
                    "format": "## 文献综述\n\n{content}",
                    "guidelines": "回顾相关研究，识别研究空白",
                    "citation_style": "APA"
                },
                "methodology": {
                    "format": "## 研究方法\n\n{content}",
                    "guidelines": "详细描述研究设计、数据收集和分析方法",
                    "structure": ["研究设计", "数据来源", "变量定义", "分析方法", "质量控制"]
                },
                "results": {
                    "format": "## 结果\n\n{content}",
                    "guidelines": "客观报告分析结果，配合图表说明",
                    "include": ["描述性统计", "推断性统计", "图表", "统计显著性"]
                },
                "discussion": {
                    "format": "## 讨论\n\n{content}",
                    "guidelines": "解释结果，讨论理论和实践意义",
                    "structure": ["结果解释", "理论意义", "实践意义", "与已有研究比较"]
                },
                "conclusion": {
                    "format": "## 结论\n\n{content}",
                    "guidelines": "总结主要发现，回答研究问题",
                    "structure": ["主要发现", "理论贡献", "实践启示"]
                },
                "limitations": {
                    "format": "## 研究局限性\n\n{content}",
                    "guidelines": "诚实说明研究的局限性和不足"
                },
                "future_research": {
                    "format": "## 未来研究方向\n\n{content}",
                    "guidelines": "基于研究发现和局限性，提出未来研究建议"
                },
                "references": {
                    "format": "## 参考文献\n\n{content}",
                    "guidelines": "按照APA格式列出所有引用文献",
                    "style": "APA"
                }
            },
            "formatting": {
                "font": "Times New Roman",
                "font_size": "12pt",
                "line_spacing": "2.0",
                "margins": "2.54cm",
                "citation_style": "APA"
            }
        }
    
    def _business_report_template(self) -> Dict[str, Any]:
        """商业报告模板"""
        return {
            "type": "business_report",
            "structure": [
                "cover_page",
                "executive_summary",
                "table_of_contents",
                "background",
                "objectives",
                "methodology",
                "key_findings",
                "detailed_analysis",
                "recommendations",
                "implementation_plan",
                "risk_assessment",
                "conclusion",
                "appendices"
            ],
            "sections": {
                "cover_page": {
                    "format": "# {title}\n\n**报告类型：** {report_type}\n**准备单位：** {organization}\n**报告日期：** {date}",
                    "elements": ["报告标题", "副标题", "准备单位", "报告日期", "机密等级"]
                },
                "executive_summary": {
                    "format": "## 执行摘要\n\n{content}",
                    "guidelines": "1-2页，高层决策者关注的核心内容",
                    "structure": ["关键发现", "主要建议", "预期影响"],
                    "word_limit": 500
                },
                "background": {
                    "format": "## 背景与现状\n\n{content}",
                    "guidelines": "描述分析背景、业务现状和分析驱动因素"
                },
                "objectives": {
                    "format": "## 分析目标\n\n{content}",
                    "guidelines": "明确分析目标和期望达成的结果"
                },
                "methodology": {
                    "format": "## 分析方法\n\n{content}",
                    "guidelines": "说明数据来源、分析工具和分析框架",
                    "structure": ["数据来源", "分析工具", "分析框架", "质量保证"]
                },
                "key_findings": {
                    "format": "## 关键发现\n\n{content}",
                    "guidelines": "用数据和图表支撑的核心发现",
                    "emphasis": "数据驱动，突出业务价值"
                },
                "detailed_analysis": {
                    "format": "## 详细分析\n\n{content}",
                    "guidelines": "深入的分析过程和结果，支撑关键发现"
                },
                "recommendations": {
                    "format": "## 建议与对策\n\n{content}",
                    "guidelines": "具体可操作的建议，包含优先级和时间轴",
                    "structure": ["短期建议", "中期规划", "长期战略"]
                },
                "implementation_plan": {
                    "format": "## 实施计划\n\n{content}",
                    "guidelines": "详细的实施步骤、时间表和责任分工"
                },
                "risk_assessment": {
                    "format": "## 风险评估\n\n{content}",
                    "guidelines": "识别潜在风险和缓解措施"
                }
            },
            "formatting": {
                "style": "商务简洁",
                "color_scheme": "蓝白色系",
                "charts": "必需",
                "language": "简洁明了"
            }
        }
    
    def _journal_article_template(self) -> Dict[str, Any]:
        """期刊论文模板"""
        return {
            "type": "journal_article",
            "structure": [
                "title",
                "authors",
                "affiliations", 
                "abstract",
                "keywords",
                "introduction",
                "materials_methods",
                "results",
                "discussion",
                "conclusions",
                "acknowledgments",
                "references",
                "author_contributions",
                "conflicts_interest",
                "funding"
            ],
            "sections": {
                "title": {
                    "format": "# {title}",
                    "guidelines": "准确、简洁，避免缩写和专业术语",
                    "word_limit": 20
                },
                "abstract": {
                    "format": "## Abstract\n\n{content}",
                    "guidelines": "结构化摘要，包含背景、方法、结果、结论",
                    "word_limit": 250,
                    "structure": ["Background", "Methods", "Results", "Conclusions"]
                },
                "keywords": {
                    "format": "**Keywords:** {keywords}",
                    "guidelines": "3-5个关键词，有助于检索",
                    "count_limit": 5
                },
                "introduction": {
                    "format": "## Introduction\n\n{content}",
                    "guidelines": "逐步缩小范围，最后提出研究假设或目标"
                },
                "materials_methods": {
                    "format": "## Materials and Methods\n\n{content}",
                    "guidelines": "足够详细，便于他人重复实验",
                    "subsections": ["Study Design", "Participants", "Data Collection", "Statistical Analysis"]
                },
                "results": {
                    "format": "## Results\n\n{content}",
                    "guidelines": "客观报告，不进行解释，配合图表",
                    "requirements": ["统计显著性", "效应量", "置信区间"]
                },
                "discussion": {
                    "format": "## Discussion\n\n{content}",
                    "guidelines": "解释结果，讨论局限性，提出未来研究方向"
                },
                "conclusions": {
                    "format": "## Conclusions\n\n{content}",
                    "guidelines": "简洁总结，呼应研究目标"
                }
            },
            "formatting": {
                "journal_style": "APA",
                "reference_style": "Vancouver",
                "word_limit": 6000,
                "figure_limit": 8,
                "table_limit": 6
            }
        }
    
    def _research_proposal_template(self) -> Dict[str, Any]:
        """研究提案模板"""
        return {
            "type": "research_proposal",
            "structure": [
                "title",
                "abstract",
                "background",
                "literature_review",
                "research_questions",
                "objectives",
                "hypotheses",
                "methodology",
                "timeline",
                "budget",
                "expected_outcomes",
                "significance",
                "references"
            ],
            "sections": {
                "research_questions": {
                    "format": "## 研究问题\n\n{content}",
                    "guidelines": "明确、具体、可研究的问题"
                },
                "objectives": {
                    "format": "## 研究目标\n\n{content}",
                    "guidelines": "具体、可测量、可达成的目标",
                    "types": ["主要目标", "次要目标"]
                },
                "hypotheses": {
                    "format": "## 研究假设\n\n{content}",
                    "guidelines": "可验证的假设陈述"
                },
                "timeline": {
                    "format": "## 研究时间表\n\n{content}",
                    "guidelines": "详细的时间安排和里程碑"
                },
                "budget": {
                    "format": "## 预算\n\n{content}",
                    "guidelines": "详细的预算分解和说明"
                },
                "expected_outcomes": {
                    "format": "## 预期成果\n\n{content}",
                    "guidelines": "预期的研究成果和贡献"
                }
            }
        }
    
    def _technical_report_template(self) -> Dict[str, Any]:
        """技术报告模板"""
        return {
            "type": "technical_report",
            "structure": [
                "title_page",
                "abstract",
                "table_of_contents",
                "introduction",
                "technical_background",
                "system_architecture",
                "implementation",
                "testing_validation",
                "results_performance",
                "discussion",
                "conclusion",
                "future_work",
                "references",
                "appendices"
            ],
            "sections": {
                "technical_background": {
                    "format": "## 技术背景\n\n{content}",
                    "guidelines": "相关技术原理和发展现状"
                },
                "system_architecture": {
                    "format": "## 系统架构\n\n{content}",
                    "guidelines": "系统设计和架构说明，配合架构图"
                },
                "implementation": {
                    "format": "## 实现方案\n\n{content}",
                    "guidelines": "具体实现方法和关键技术"
                },
                "testing_validation": {
                    "format": "## 测试与验证\n\n{content}",
                    "guidelines": "测试方法、测试用例和验证结果"
                },
                "results_performance": {
                    "format": "## 结果与性能\n\n{content}",
                    "guidelines": "性能指标、测试结果和分析"
                }
            }
        }
    
    def _executive_summary_template(self) -> Dict[str, Any]:
        """执行摘要模板"""
        return {
            "type": "executive_summary",
            "structure": [
                "headline",
                "key_findings",
                "recommendations",
                "business_impact",
                "next_steps"
            ],
            "sections": {
                "headline": {
                    "format": "# {title}",
                    "guidelines": "吸引眼球的标题，突出核心价值"
                },
                "key_findings": {
                    "format": "## 关键发现\n\n{content}",
                    "guidelines": "最重要的3-5个发现，用数据支撑",
                    "format_style": "bullet_points"
                },
                "recommendations": {
                    "format": "## 核心建议\n\n{content}",
                    "guidelines": "具体可操作的建议，包含优先级"
                },
                "business_impact": {
                    "format": "## 业务影响\n\n{content}",
                    "guidelines": "量化的业务价值和影响"
                },
                "next_steps": {
                    "format": "## 下一步行动\n\n{content}",
                    "guidelines": "明确的行动计划和时间表"
                }
            },
            "formatting": {
                "length": "1-2页",
                "style": "简洁有力",
                "visual_elements": "图表和关键数据"
            }
        }
    
    def _default_template(self) -> Dict[str, Any]:
        """默认模板"""
        return {
            "type": "default",
            "structure": [
                "title",
                "summary",
                "introduction",
                "analysis",
                "results",
                "conclusion"
            ],
            "sections": {
                "title": {
                    "format": "# {title}",
                    "guidelines": "简洁明了的标题"
                },
                "summary": {
                    "format": "## 摘要\n\n{content}",
                    "guidelines": "简要概述报告内容"
                },
                "introduction": {
                    "format": "## 引言\n\n{content}",
                    "guidelines": "介绍背景和目的"
                },
                "analysis": {
                    "format": "## 分析\n\n{content}",
                    "guidelines": "详细的分析过程"
                },
                "results": {
                    "format": "## 结果\n\n{content}",
                    "guidelines": "分析结果和发现"
                },
                "conclusion": {
                    "format": "## 结论\n\n{content}",
                    "guidelines": "总结和建议"
                }
            }
        }
    
    def generate_template_structure(self, template_type: str, custom_sections: Optional[Dict] = None) -> str:
        """生成模板结构"""
        template = self.get_template(template_type)
        
        if custom_sections:
            template["sections"].update(custom_sections)
        
        structure = []
        for section_name in template["structure"]:
            if section_name in template["sections"]:
                section_info = template["sections"][section_name]
                structure.append(f"## {section_name.replace('_', ' ').title()}")
                structure.append(f"格式: {section_info.get('format', '')}")
                structure.append(f"指导: {section_info.get('guidelines', '')}")
                structure.append("")
        
        return "\n".join(structure)
    
    def validate_template_compliance(self, content: Dict, template_type: str) -> Dict[str, Any]:
        """验证模板合规性"""
        template = self.get_template(template_type)
        compliance_report = {
            "compliant": True,
            "missing_sections": [],
            "issues": [],
            "suggestions": []
        }
        
        # 检查必需章节
        required_sections = template["structure"]
        provided_sections = list(content.keys())
        
        for section in required_sections:
            if section not in provided_sections:
                compliance_report["missing_sections"].append(section)
                compliance_report["compliant"] = False
        
        # 检查字数限制
        for section_name, section_content in content.items():
            if section_name in template["sections"]:
                section_template = template["sections"][section_name]
                if "word_limit" in section_template:
                    word_count = len(section_content.split())
                    if word_count > section_template["word_limit"]:
                        compliance_report["issues"].append(
                            f"{section_name}超出字数限制: {word_count}/{section_template['word_limit']}"
                        )
        
        return compliance_report

# 预定义的报告样例
SAMPLE_REPORTS = {
    "academic_data_analysis": {
        "title": "基于大数据的消费者行为分析研究",
        "abstract": "本研究基于大规模消费者交易数据，运用机器学习方法分析消费者行为模式。研究发现消费者购买决策受到季节性、价格敏感性和品牌偏好等多重因素影响。研究结果为企业制定精准营销策略提供了科学依据。",
        "keywords": ["消费者行为", "大数据分析", "机器学习", "营销策略"],
        "methodology": "采用聚类分析、关联规则挖掘和预测建模等方法，对50万条消费记录进行深度分析。",
        "key_findings": [
            "季节性因素对消费行为影响显著(p<0.001)",
            "价格敏感度在不同消费群体间存在显著差异",
            "品牌忠诚度与消费频次呈正相关关系(r=0.73)"
        ]
    },
    "business_sales_analysis": {
        "title": "2024年第三季度销售数据分析报告",
        "executive_summary": "本季度销售额同比增长15.2%，环比增长8.7%。线上渠道表现突出，移动端销售占比首次突破60%。建议加大移动端投入，优化用户体验。",
        "key_metrics": {
            "total_sales": "¥5,240万",
            "growth_rate": "15.2%",
            "mobile_percentage": "62.3%",
            "customer_acquisition": "12,450人"
        },
        "recommendations": [
            "增加移动端运营人员配置",
            "优化移动购物流程",
            "加强社交媒体营销投入"
        ]
    }
}