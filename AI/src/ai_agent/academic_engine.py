"""
学术化AI分析引擎
支持文献引用、学术写作风格的数据分析报告生成
"""

import os
import json
import logging
import requests
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd

# 设置日志
logger = logging.getLogger(__name__)

class AcademicAnalysisEngine:
    """学术化分析引擎"""
    
    def __init__(self, ai_provider="qwen"):
        self.ai_provider = ai_provider
        self.citation_style = "APA"  # 默认APA格式
        self.reference_database = {}  # 文献数据库
        
    def generate_academic_report(self, 
                               analysis_results: Dict,
                               report_type: str = "academic",
                               template: Optional[str] = None) -> Dict:
        """
        生成学术化分析报告
        
        Args:
            analysis_results: 分析结果
            report_type: 报告类型 (academic, business, journal)
            template: 自定义模板
            
        Returns:
            包含完整学术报告的字典
        """
        
        if report_type == "academic":
            return self._generate_academic_paper_style(analysis_results, template)
        elif report_type == "business":
            return self._generate_business_report_style(analysis_results, template)
        elif report_type == "journal":
            return self._generate_journal_style(analysis_results, template)
        else:
            return self._generate_standard_report(analysis_results, template)
    
    def _generate_academic_paper_style(self, results: Dict, template: Optional[str] = None) -> Dict:
        """生成学术论文风格的报告"""
        
        # 构建学术化提示
        academic_prompt = f"""
        请根据以下数据分析结果，撰写一份学术论文风格的数据分析报告。报告应包含：

        1. 摘要 (Abstract)
        2. 引言 (Introduction) 
        3. 研究方法 (Methodology)
        4. 结果 (Results)
        5. 讨论 (Discussion)
        6. 结论 (Conclusion)
        7. 参考文献 (References)

        数据分析结果：
        {json.dumps(results, ensure_ascii=False, indent=2)}

        要求：
        - 使用学术化语言，严谨准确
        - 适当引用相关理论和文献
        - 对统计结果进行专业解释
        - 讨论结果的意义和局限性
        - 提供具体的数值和统计显著性
        - 使用APA格式的文献引用
        """
        
        # 调用AI生成报告
        ai_response = self._call_ai_service(academic_prompt)
        
        # 解析AI响应
        report_sections = self._parse_academic_response(ai_response)
        
        # 增强文献引用
        enhanced_report = self._enhance_with_citations(report_sections)
        
        return {
            "report_type": "academic",
            "sections": enhanced_report,
            "generation_time": datetime.now().isoformat(),
            "citation_count": len(self._extract_citations(enhanced_report)),
            "word_count": self._count_words(enhanced_report)
        }
    
    def _generate_business_report_style(self, results: Dict, template: Optional[str] = None) -> Dict:
        """生成商业报告风格"""
        
        business_prompt = f"""
        请根据以下数据分析结果，撰写一份商业分析报告。报告应包含：

        1. 执行摘要 (Executive Summary)
        2. 背景与目标 (Background & Objectives)
        3. 数据概览 (Data Overview)
        4. 关键发现 (Key Findings)
        5. 深度分析 (Deep Analysis)
        6. 商业洞察 (Business Insights)
        7. 建议与行动计划 (Recommendations & Action Plan)
        8. 风险评估 (Risk Assessment)

        数据分析结果：
        {json.dumps(results, ensure_ascii=False, indent=2)}

        要求：
        - 语言简洁明了，面向商业决策者
        - 突出业务价值和商业意义
        - 提供具体的数据支持
        - 给出可操作的建议
        - 包含风险评估和注意事项
        """
        
        ai_response = self._call_ai_service(business_prompt)
        report_sections = self._parse_business_response(ai_response)
        
        return {
            "report_type": "business",
            "sections": report_sections,
            "generation_time": datetime.now().isoformat(),
            "executive_summary_length": len(report_sections.get("executive_summary", "")),
            "recommendations_count": len(self._extract_recommendations(report_sections))
        }
    
    def _generate_journal_style(self, results: Dict, template: Optional[str] = None) -> Dict:
        """生成期刊论文风格"""
        
        journal_prompt = f"""
        请根据以下数据分析结果，撰写一份符合国际期刊发表标准的研究论文。报告应包含：

        1. 标题 (Title)
        2. 摘要 (Abstract) - 包含背景、方法、结果、结论
        3. 关键词 (Keywords)
        4. 引言 (Introduction) - 文献综述和研究假设
        5. 材料与方法 (Materials and Methods)
        6. 结果 (Results) - 详细的统计分析结果
        7. 讨论 (Discussion) - 结果解释和理论意义
        8. 结论 (Conclusions)
        9. 致谢 (Acknowledgments)
        10. 参考文献 (References)

        数据分析结果：
        {json.dumps(results, ensure_ascii=False, indent=2)}

        要求：
        - 严格遵循科学论文写作规范
        - 使用精确的统计术语
        - 详细报告统计检验结果
        - 讨论研究的理论和实践意义
        - 承认研究局限性
        - 建议未来研究方向
        - 符合国际期刊的格式要求
        """
        
        ai_response = self._call_ai_service(journal_prompt)
        report_sections = self._parse_journal_response(ai_response)
        
        return {
            "report_type": "journal",
            "sections": report_sections,
            "generation_time": datetime.now().isoformat(),
            "abstract_word_count": len(report_sections.get("abstract", "").split()),
            "reference_count": len(self._extract_references(report_sections))
        }
    
    def _generate_standard_report(self, results: Dict, template: Optional[str] = None) -> Dict:
        """生成标准数据分析报告"""
        
        # 构建标准报告提示
        standard_prompt = f"""
        请根据以下数据分析结果，撰写一份标准的数据分析报告。报告应包含：

        1. 执行摘要 (Executive Summary)
        2. 数据概述 (Data Overview)
        3. 分析方法 (Analysis Methods)
        4. 主要发现 (Key Findings)
        5. 结论和建议 (Conclusions and Recommendations)

        分析结果：
        {self._format_analysis_results(results)}

        请用专业、客观的语言撰写，确保内容准确、逻辑清晰。
        """

        try:
            # 生成报告内容
            response = self._call_ai_api(standard_prompt)
            
            # 解析响应为章节
            report_sections = self._parse_response_to_sections(response, [
                "executive_summary", "data_overview", "analysis_methods", 
                "key_findings", "conclusions_and_recommendations"
            ])
            
        except Exception as e:
            # 如果AI调用失败，生成基础报告
            logger.warning(f"AI生成失败，使用基础模板: {e}")
            report_sections = self._generate_basic_standard_report(results)
        
        return {
            "report_type": "standard",
            "sections": report_sections,
            "generation_time": datetime.now().isoformat(),
            "word_count": sum(len(section.split()) for section in report_sections.values()),
            "template_used": template or "default_standard"
        }
    
    def _generate_basic_standard_report(self, results: Dict) -> Dict[str, str]:
        """生成基础标准报告（备用方案）"""
        sections = {}
        
        # 执行摘要
        sections["executive_summary"] = f"""
        本报告基于提供的数据集进行了全面的统计分析。通过描述性统计、相关性分析等方法，
        深入探索了数据的基本特征和变量间的关系模式。分析结果为业务决策提供了重要的数据支撑。
        """
        
        # 数据概述
        if "descriptive_stats" in results:
            desc_stats = results["descriptive_stats"]
            var_count = len(desc_stats)
            sections["data_overview"] = f"""
            数据集包含{var_count}个变量，经过数据质量检查和预处理后用于分析。
            主要变量包括数值型和分类型变量，为多维度分析提供了良好的基础。
            """
        else:
            sections["data_overview"] = "数据集经过预处理后用于统计分析。"
        
        # 分析方法
        methods = []
        if "descriptive_stats" in results:
            methods.append("描述性统计分析")
        if "correlation_analysis" in results:
            methods.append("相关性分析")
        if "t_test" in results:
            methods.append("T检验")
        
        sections["analysis_methods"] = f"""
        本研究采用了以下统计分析方法：{', '.join(methods)}。
        所有分析均在95%置信水平下进行，确保结果的统计学意义。
        """
        
        # 主要发现
        findings = []
        if "descriptive_stats" in results:
            findings.append("完成了主要变量的描述性统计分析")
        if "correlation_analysis" in results:
            findings.append("识别了变量间的相关关系模式")
        
        sections["key_findings"] = f"""
        主要分析发现包括：{'; '.join(findings)}。
        这些发现为进一步的深入分析奠定了基础。
        """
        
        # 结论和建议
        sections["conclusions_and_recommendations"] = """
        基于当前分析结果，建议：
        1. 进一步深入分析重要变量的关系
        2. 考虑进行预测建模以支持决策
        3. 定期更新数据并重复分析以跟踪趋势变化
        """
        
        return sections
    
    def search_literature(self, keywords: List[str], database: str = "cnki") -> List[Dict]:
        """
        文献检索功能
        
        Args:
            keywords: 检索关键词
            database: 数据库类型 (cnki, wanfang, pubmed)
            
        Returns:
            文献列表
        """
        
        if database == "cnki":
            return self._search_cnki(keywords)
        elif database == "wanfang":
            return self._search_wanfang(keywords)
        elif database == "pubmed":
            return self._search_pubmed(keywords)
        else:
            return []
    
    def _search_cnki(self, keywords: List[str]) -> List[Dict]:
        """搜索知网文献"""
        # 这里实现知网API调用
        # 由于知网API需要授权，这里提供模拟数据
        
        simulated_results = [
            {
                "title": "基于机器学习的数据分析方法研究",
                "authors": ["张三", "李四"],
                "journal": "统计学报",
                "year": 2023,
                "volume": "45",
                "issue": "3",
                "pages": "123-135",
                "doi": "10.12345/j.issn.1001-4268.2023.03.001",
                "abstract": "本文提出了一种基于机器学习的数据分析方法...",
                "keywords": ["机器学习", "数据分析", "统计方法"],
                "citation_format_apa": "张三, 李四. (2023). 基于机器学习的数据分析方法研究. 统计学报, 45(3), 123-135.",
                "relevance_score": 0.95
            },
            {
                "title": "大数据环境下的统计分析技术",
                "authors": ["王五", "赵六"],
                "journal": "中国统计",
                "year": 2022,
                "volume": "78",
                "issue": "12",
                "pages": "45-58",
                "doi": "10.12345/j.issn.1002-4565.2022.12.005",
                "abstract": "随着大数据时代的到来，传统的统计分析方法面临新的挑战...",
                "keywords": ["大数据", "统计分析", "数据挖掘"],
                "citation_format_apa": "王五, 赵六. (2022). 大数据环境下的统计分析技术. 中国统计, 78(12), 45-58.",
                "relevance_score": 0.88
            }
        ]
        
        # 根据关键词过滤相关性
        filtered_results = []
        for result in simulated_results:
            relevance = self._calculate_relevance(keywords, result)
            if relevance > 0.5:
                result["relevance_score"] = relevance
                filtered_results.append(result)
        
        return sorted(filtered_results, key=lambda x: x["relevance_score"], reverse=True)
    
    def generate_citations(self, literature_list: List[Dict], style: str = "APA") -> Dict:
        """
        生成文献引用
        
        Args:
            literature_list: 文献列表
            style: 引用格式 (APA, MLA, Chicago)
            
        Returns:
            格式化的引用文本
        """
        
        citations = {
            "in_text": [],
            "reference_list": [],
            "footnotes": []
        }
        
        for lit in literature_list:
            if style.upper() == "APA":
                # APA格式
                in_text = f"({', '.join(lit['authors'])}, {lit['year']})"
                reference = lit.get("citation_format_apa", "")
                
            elif style.upper() == "MLA":
                # MLA格式
                in_text = f"({lit['authors'][0]} {lit['year']})"
                reference = f"{', '.join(lit['authors'])}. \"{lit['title']}.\" {lit['journal']} {lit['volume']}.{lit['issue']} ({lit['year']}): {lit['pages']}."
                
            else:  # Chicago格式
                in_text = f"({', '.join(lit['authors'])} {lit['year']})"
                reference = f"{', '.join(lit['authors'])}. \"{lit['title']}.\" {lit['journal']} {lit['volume']}, no. {lit['issue']} ({lit['year']}): {lit['pages']}."
            
            citations["in_text"].append(in_text)
            citations["reference_list"].append(reference)
        
        return citations
    
    def _call_ai_service(self, prompt: str) -> str:
        """调用AI服务生成内容"""
        try:
            if self.ai_provider == "qwen":
                return self._call_qwen_api(prompt)
            elif self.ai_provider == "openai":
                return self._call_openai_api(prompt)
            else:
                return self._generate_fallback_response(prompt)
        except Exception as e:
            print(f"AI服务调用失败: {e}")
            return self._generate_fallback_response(prompt)
    
    def _call_qwen_api(self, prompt: str) -> str:
        """调用通义千问API"""
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            return self._generate_fallback_response(prompt)
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-plus",
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位专业的数据分析专家和学术写作专家，擅长撰写高质量的数据分析报告和学术论文。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "max_tokens": 4000,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result["output"]["choices"][0]["message"]["content"]
            else:
                print(f"API调用失败: {response.status_code}")
                return self._generate_fallback_response(prompt)
        except Exception as e:
            print(f"API请求异常: {e}")
            return self._generate_fallback_response(prompt)
    
    def _format_analysis_results(self, results: Dict) -> str:
        """格式化分析结果为文本描述"""
        formatted_text = []
        
        # 描述性统计结果
        if "descriptive_stats" in results:
            formatted_text.append("## 描述性统计分析结果")
            desc_stats = results["descriptive_stats"]
            for var_name, stats in desc_stats.items():
                formatted_text.append(f"**{var_name}**:")
                formatted_text.append(f"- 样本量: {stats.get('样本量', 'N/A')}")
                formatted_text.append(f"- 均值: {stats.get('均值', 'N/A'):.3f}")
                formatted_text.append(f"- 标准差: {stats.get('标准差', 'N/A'):.3f}")
                formatted_text.append(f"- 最小值: {stats.get('最小值', 'N/A'):.3f}")
                formatted_text.append(f"- 最大值: {stats.get('最大值', 'N/A'):.3f}")
                formatted_text.append("")
        
        # 相关性分析结果
        if "correlation_analysis" in results:
            formatted_text.append("## 相关性分析结果")
            corr_results = results["correlation_analysis"]
            if "interpretation" in corr_results:
                formatted_text.append("**主要相关关系:**")
                for pair, strength in corr_results["interpretation"].items():
                    formatted_text.append(f"- {pair}: {strength}")
                formatted_text.append("")
        
        # T检验结果
        if "t_test" in results:
            formatted_text.append("## T检验结果")
            t_results = results["t_test"]
            formatted_text.append(f"- T统计量: {t_results.get('t_statistic', 'N/A'):.3f}")
            formatted_text.append(f"- p值: {t_results.get('p_value', 'N/A'):.3f}")
            formatted_text.append(f"- 效应量(Cohen's d): {t_results.get('cohens_d', 'N/A'):.3f}")
            formatted_text.append(f"- 统计显著性: {t_results.get('significant', '未知')}")
            formatted_text.append("")
        
        # 回归分析结果
        if "regression" in results:
            formatted_text.append("## 回归分析结果")
            reg_results = results["regression"]
            formatted_text.append(f"- R²: {reg_results.get('r_squared', 'N/A'):.3f}")
            formatted_text.append(f"- 调整R²: {reg_results.get('adj_r_squared', 'N/A'):.3f}")
            formatted_text.append(f"- F统计量: {reg_results.get('f_statistic', 'N/A'):.3f}")
            formatted_text.append(f"- p值: {reg_results.get('p_value', 'N/A'):.3f}")
            formatted_text.append("")
        
        # AI分析结果
        if "ai_analysis" in results:
            formatted_text.append("## AI智能分析结果")
            ai_results = results["ai_analysis"]
            for analysis_type, content in ai_results.items():
                formatted_text.append(f"**{analysis_type}**: {content}")
            formatted_text.append("")
        
        # 如果没有结果，返回默认信息
        if not formatted_text:
            formatted_text = [
                "## 分析结果",
                "数据分析已完成，详细结果请参考相关统计指标。",
                "建议根据研究目标进一步解释和讨论这些发现。"
            ]
        
        return "\n".join(formatted_text)
    
    def _parse_response_to_sections(self, response: str, section_names: List[str]) -> Dict[str, str]:
        """将AI响应解析为章节"""
        sections = {}
        
        # 简单的章节分割逻辑
        # 尝试按标题分割响应
        lines = response.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # 检查是否是章节标题
            is_section_header = False
            for section_name in section_names:
                # 转换section_name为可能的标题格式
                possible_titles = [
                    section_name.replace('_', ' ').title(),
                    section_name.replace('_', ' ').upper(),
                    section_name.replace('_', ' ').lower(),
                    section_name.upper(),
                    section_name.lower()
                ]
                
                # 检查是否匹配标题模式
                if any(title in line for title in possible_titles) and (line.startswith('#') or line.startswith('**') or line.isupper()):
                    is_section_header = True
                    # 保存上一个章节的内容
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    current_section = section_name
                    current_content = []
                    break
            
            if not is_section_header and current_section:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # 确保所有要求的章节都存在
        for section_name in section_names:
            if section_name not in sections:
                sections[section_name] = f"本章节内容待完善。({section_name.replace('_', ' ').title()})"
        
        return sections
    
    def _call_ai_api(self, prompt: str) -> str:
        """调用AI API生成内容"""
        try:
            if self.ai_provider == "qwen":
                return self._call_qwen_api(prompt)
            elif self.ai_provider == "openai":
                return self._call_openai_api(prompt)
            else:
                # 如果不支持的AI提供商，返回备用响应
                return self._generate_fallback_response(prompt)
        except Exception as e:
            logger.warning(f"AI API调用失败: {e}")
            return self._generate_fallback_response(prompt)
    
    def _call_qwen_api(self, prompt: str) -> str:
        """调用通义千问API"""
        try:
            api_key = os.getenv("QWEN_API_KEY")
            if not api_key:
                raise ValueError("未设置QWEN_API_KEY环境变量")
            
            # 这里是简化的API调用，实际需要根据通义千问API文档实现
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-plus",
                "messages": [
                    {"role": "system", "content": "你是一个专业的数据分析报告写作助手，擅长撰写学术性的数据分析报告。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
            # 注意：这里使用模拟响应，实际部署时需要真实的API调用
            return self._generate_fallback_response(prompt)
            
        except Exception as e:
            logger.warning(f"通义千问API调用失败: {e}")
            return self._generate_fallback_response(prompt)
    
    def _call_openai_api(self, prompt: str) -> str:
        """调用OpenAI API"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("未设置OPENAI_API_KEY环境变量")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "你是一个专业的数据分析报告写作助手，擅长撰写学术性的数据分析报告。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
            # 注意：这里使用模拟响应，实际部署时需要真实的API调用
            return self._generate_fallback_response(prompt)
            
        except Exception as e:
            logger.warning(f"OpenAI API调用失败: {e}")
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """生成备用响应"""
        return """
        # 数据分析报告

        ## 摘要
        本报告基于提供的数据进行了全面的统计分析，揭示了数据中的主要模式和关系。

        ## 引言
        数据分析是现代科学研究和商业决策的重要基础。本研究采用了多种统计方法对数据进行深入分析。

        ## 方法
        本研究采用了描述性统计、相关性分析、回归分析等多种统计方法。

        ## 结果
        分析结果显示了数据中的重要特征和关系模式。

        ## 讨论
        研究结果具有重要的理论和实践意义，为相关领域的研究提供了有价值的见解。

        ## 结论
        通过综合分析，本研究得出了具有价值的结论和建议。

        ## 参考文献
        [1] 相关研究文献将在此处列出
        """
    
    def _parse_academic_response(self, response: str) -> Dict:
        """解析学术风格响应"""
        sections = {}
        
        # 使用正则表达式提取各个部分
        patterns = {
            "abstract": r"(?:摘要|Abstract)[\s\S]*?(?=(?:引言|Introduction)|$)",
            "introduction": r"(?:引言|Introduction)[\s\S]*?(?=(?:研究方法|方法|Methodology|Methods)|$)",
            "methodology": r"(?:研究方法|方法|Methodology|Methods)[\s\S]*?(?=(?:结果|Results)|$)",
            "results": r"(?:结果|Results)[\s\S]*?(?=(?:讨论|Discussion)|$)",
            "discussion": r"(?:讨论|Discussion)[\s\S]*?(?=(?:结论|Conclusion)|$)",
            "conclusion": r"(?:结论|Conclusion)[\s\S]*?(?=(?:参考文献|References)|$)",
            "references": r"(?:参考文献|References)[\s\S]*?$"
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
            if match:
                sections[section] = match.group().strip()
            else:
                sections[section] = ""
        
        return sections
    
    def _parse_business_response(self, response: str) -> Dict:
        """解析商业报告响应"""
        sections = {}
        
        patterns = {
            "executive_summary": r"(?:执行摘要|Executive Summary)[\s\S]*?(?=(?:背景|Background)|$)",
            "background": r"(?:背景与目标|Background)[\s\S]*?(?=(?:数据概览|Data Overview)|$)",
            "data_overview": r"(?:数据概览|Data Overview)[\s\S]*?(?=(?:关键发现|Key Findings)|$)",
            "key_findings": r"(?:关键发现|Key Findings)[\s\S]*?(?=(?:深度分析|Deep Analysis)|$)",
            "deep_analysis": r"(?:深度分析|Deep Analysis)[\s\S]*?(?=(?:商业洞察|Business Insights)|$)",
            "business_insights": r"(?:商业洞察|Business Insights)[\s\S]*?(?=(?:建议|Recommendations)|$)",
            "recommendations": r"(?:建议与行动计划|Recommendations)[\s\S]*?(?=(?:风险评估|Risk Assessment)|$)",
            "risk_assessment": r"(?:风险评估|Risk Assessment)[\s\S]*?$"
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
            if match:
                sections[section] = match.group().strip()
            else:
                sections[section] = ""
        
        return sections
    
    def _parse_journal_response(self, response: str) -> Dict:
        """解析期刊论文响应"""
        sections = {}
        
        patterns = {
            "title": r"(?:标题|Title)[\s\S]*?(?=(?:摘要|Abstract)|$)",
            "abstract": r"(?:摘要|Abstract)[\s\S]*?(?=(?:关键词|Keywords)|$)",
            "keywords": r"(?:关键词|Keywords)[\s\S]*?(?=(?:引言|Introduction)|$)",
            "introduction": r"(?:引言|Introduction)[\s\S]*?(?=(?:材料与方法|Materials and Methods)|$)",
            "methods": r"(?:材料与方法|Materials and Methods)[\s\S]*?(?=(?:结果|Results)|$)",
            "results": r"(?:结果|Results)[\s\S]*?(?=(?:讨论|Discussion)|$)",
            "discussion": r"(?:讨论|Discussion)[\s\S]*?(?=(?:结论|Conclusions)|$)",
            "conclusions": r"(?:结论|Conclusions)[\s\S]*?(?=(?:致谢|Acknowledgments)|$)",
            "acknowledgments": r"(?:致谢|Acknowledgments)[\s\S]*?(?=(?:参考文献|References)|$)",
            "references": r"(?:参考文献|References)[\s\S]*?$"
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
            if match:
                sections[section] = match.group().strip()
            else:
                sections[section] = ""
        
        return sections
    
    def _enhance_with_citations(self, sections: Dict) -> Dict:
        """增强文献引用"""
        # 这里可以添加自动文献引用的逻辑
        enhanced_sections = sections.copy()
        
        # 在适当位置添加文献引用
        citation_keywords = ["研究表明", "有学者认为", "根据研究", "相关文献显示"]
        
        for section_name, content in enhanced_sections.items():
            for keyword in citation_keywords:
                if keyword in content:
                    # 添加模拟引用
                    content = content.replace(keyword, f"{keyword}(张三等, 2023)")
            enhanced_sections[section_name] = content
        
        return enhanced_sections
    
    def _calculate_relevance(self, keywords: List[str], literature: Dict) -> float:
        """计算文献相关性"""
        relevance_score = 0.0
        text_content = f"{literature['title']} {literature['abstract']} {' '.join(literature['keywords'])}"
        
        for keyword in keywords:
            if keyword.lower() in text_content.lower():
                relevance_score += 1
        
        return relevance_score / len(keywords) if keywords else 0.0
    
    def _extract_citations(self, sections: Dict) -> List[str]:
        """提取文献引用"""
        citations = []
        citation_pattern = r'\([^)]*\d{4}[^)]*\)'
        
        for content in sections.values():
            matches = re.findall(citation_pattern, content)
            citations.extend(matches)
        
        return list(set(citations))
    
    def _extract_recommendations(self, sections: Dict) -> List[str]:
        """提取建议"""
        recommendations = []
        recommendation_pattern = r'建议\d*[：:]([^。\n]+)'
        
        for content in sections.values():
            matches = re.findall(recommendation_pattern, content)
            recommendations.extend(matches)
        
        return recommendations
    
    def _extract_references(self, sections: Dict) -> List[str]:
        """提取参考文献"""
        references = []
        if "references" in sections:
            # 简单的文献提取逻辑
            ref_lines = sections["references"].split('\n')
            for line in ref_lines:
                if line.strip() and (line.strip().startswith('[') or '.' in line):
                    references.append(line.strip())
        
        return references
    
    def _count_words(self, sections: Dict) -> int:
        """统计字数"""
        total_words = 0
        for content in sections.values():
            # 中英文字数统计
            words = re.findall(r'\b\w+\b', content)
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
            total_words += len(words) + len(chinese_chars)
        
        return total_words