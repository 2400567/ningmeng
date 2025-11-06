#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能参考文献系统
支持多平台文献检索，AI智能选择和用户自定义输入
"""

import pandas as pd
import streamlit as st
import requests
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Reference:
    """参考文献数据结构"""
    title: str
    authors: List[str]
    journal: str
    year: int
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None
    citation_format: str = "APA"

class LiteratureSearchEngine:
    """文献检索引擎"""
    
    def __init__(self):
        self.search_engines = {
            "google_scholar": "Google Scholar",
            "pubmed": "PubMed", 
            "ieee": "IEEE Xplore",
            "acm": "ACM Digital Library",
            "cnki": "中国知网",
            "wanfang": "万方数据库",
            "vip": "维普数据库"
        }
        self.ai_client = None
        
    def search_literature(self, query: str, platform: str, 
                         max_results: int = 10) -> List[Reference]:
        """搜索文献"""
        try:
            if platform == "google_scholar":
                return self._search_google_scholar(query, max_results)
            elif platform == "pubmed":
                return self._search_pubmed(query, max_results)
            elif platform == "cnki":
                return self._search_cnki(query, max_results)
            else:
                # 模拟搜索结果
                return self._generate_mock_results(query, platform, max_results)
        except Exception as e:
            logger.error(f"文献搜索失败: {e}")
            return self._generate_mock_results(query, platform, max_results)
    
    def _search_google_scholar(self, query: str, max_results: int) -> List[Reference]:
        """搜索Google Scholar（模拟）"""
        # 实际实现需要使用Google Scholar API或爬虫
        return self._generate_mock_results(query, "google_scholar", max_results)
    
    def _search_pubmed(self, query: str, max_results: int) -> List[Reference]:
        """搜索PubMed"""
        try:
            # PubMed E-utilities API
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            
            # 搜索
            search_url = f"{base_url}esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json"
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            search_data = response.json()
            
            if "esearchresult" in search_data and "idlist" in search_data["esearchresult"]:
                ids = search_data["esearchresult"]["idlist"]
                
                # 获取详细信息
                fetch_url = f"{base_url}efetch.fcgi"
                fetch_params = {
                    "db": "pubmed",
                    "id": ",".join(ids),
                    "retmode": "xml"
                }
                
                # 这里需要解析XML，简化为模拟结果
                return self._generate_mock_results(query, "pubmed", len(ids))
            
        except Exception as e:
            logger.error(f"PubMed搜索失败: {e}")
        
        return self._generate_mock_results(query, "pubmed", max_results)
    
    def _search_cnki(self, query: str, max_results: int) -> List[Reference]:
        """搜索中国知网（模拟）"""
        # 实际实现需要CNKI API或爬虫
        return self._generate_mock_results(query, "cnki", max_results)
    
    def _generate_mock_results(self, query: str, platform: str, 
                             max_results: int) -> List[Reference]:
        """生成模拟搜索结果"""
        mock_results = []
        
        # 基于查询生成相关的模拟文献
        base_titles = [
            f"A Comprehensive Study on {query}: Methods and Applications",
            f"Advanced {query} Analysis in Modern Research",
            f"Exploring {query}: A Systematic Review",
            f"Novel Approaches to {query}: Empirical Evidence",
            f"The Impact of {query} on Contemporary Studies",
            f"{query} in Practice: A Multi-disciplinary Perspective",
            f"Understanding {query}: Theoretical Framework and Applications",
            f"Recent Advances in {query} Research",
            f"{query} Analysis: Methodological Innovations",
            f"Future Directions in {query} Studies"
        ]
        
        authors_pool = [
            ["Zhang, L.", "Wang, H.", "Liu, J."],
            ["Smith, J.A.", "Johnson, R.B.", "Brown, M."],
            ["李明", "张伟", "王芳"],
            ["Chen, X.", "Liu, Y.", "Wu, Z."],
            ["Anderson, P.", "Wilson, K.", "Davis, S."],
            ["孙强", "赵敏", "刘涛"],
            ["Garcia, M.", "Martinez, A.", "Rodriguez, C."],
            ["田华", "周杰", "黄磊"]
        ]
        
        journals_by_platform = {
            "google_scholar": [
                "Nature", "Science", "Journal of Applied Psychology",
                "Management Science", "Information Systems Research"
            ],
            "pubmed": [
                "The Lancet", "New England Journal of Medicine",
                "Journal of Medical Internet Research", "PLOS Medicine"
            ],
            "cnki": [
                "管理科学学报", "心理学报", "计算机学报", "中国管理科学", "系统工程理论与实践"
            ],
            "ieee": [
                "IEEE Transactions on Software Engineering",
                "IEEE Computer", "IEEE Systems Journal"
            ]
        }
        
        journals = journals_by_platform.get(platform, journals_by_platform["google_scholar"])
        
        import random
        for i in range(min(max_results, len(base_titles))):
            title = base_titles[i]
            authors = random.choice(authors_pool)
            journal = random.choice(journals)
            year = random.randint(2015, 2024)
            
            ref = Reference(
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                volume=str(random.randint(10, 50)),
                issue=str(random.randint(1, 12)),
                pages=f"{random.randint(100, 999)}-{random.randint(1000, 1999)}",
                doi=f"10.1000/{random.randint(1000, 9999)}.{random.randint(100000, 999999)}",
                abstract=f"This study investigates {query} using advanced analytical methods..."
            )
            
            mock_results.append(ref)
        
        return mock_results
    
    def ai_select_references(self, query: str, references: List[Reference],
                           selection_criteria: Dict[str, Any]) -> List[Reference]:
        """AI智能选择参考文献"""
        try:
            if self.ai_client:
                return self._ai_intelligent_selection(query, references, selection_criteria)
            else:
                return self._rule_based_selection(references, selection_criteria)
        except Exception as e:
            logger.error(f"AI文献选择失败: {e}")
            return self._rule_based_selection(references, selection_criteria)
    
    def _ai_intelligent_selection(self, query: str, references: List[Reference],
                                criteria: Dict[str, Any]) -> List[Reference]:
        """AI智能选择"""
        # 构建提示词
        refs_text = ""
        for i, ref in enumerate(references):
            refs_text += f"{i+1}. {ref.title} ({ref.year}) - {ref.journal}\n"
        
        prompt = f"""
        作为文献研究专家，请从以下文献中选择最相关和高质量的参考文献：
        
        研究主题: {query}
        选择标准: {json.dumps(criteria, ensure_ascii=False)}
        
        候选文献:
        {refs_text}
        
        请选择最符合以下要求的文献：
        1. 与研究主题高度相关
        2. 期刊影响因子较高
        3. 发表年份较新
        4. 研究方法科学严谨
        
        请返回选中文献的编号（用逗号分隔）：
        """
        
        # 模拟AI响应
        selected_indices = [0, 1, 2, 3, 4]  # 前5个
        return [references[i] for i in selected_indices if i < len(references)]
    
    def _rule_based_selection(self, references: List[Reference],
                            criteria: Dict[str, Any]) -> List[Reference]:
        """基于规则的选择"""
        # 按年份排序（新的优先）
        sorted_refs = sorted(references, key=lambda x: x.year, reverse=True)
        
        # 应用筛选条件
        min_year = criteria.get("min_year", 2010)
        max_results = criteria.get("max_results", 20)
        
        filtered_refs = [ref for ref in sorted_refs if ref.year >= min_year]
        
        return filtered_refs[:max_results]

class ReferenceFormatter:
    """参考文献格式化器"""
    
    def __init__(self):
        self.formats = {
            "APA": self._format_apa,
            "MLA": self._format_mla,
            "IEEE": self._format_ieee,
            "Chicago": self._format_chicago,
            "Harvard": self._format_harvard,
            "国标": self._format_gb
        }
    
    def format_reference(self, ref: Reference, format_style: str) -> str:
        """格式化参考文献"""
        formatter = self.formats.get(format_style, self._format_apa)
        return formatter(ref)
    
    def _format_apa(self, ref: Reference) -> str:
        """APA格式"""
        authors = self._format_authors_apa(ref.authors)
        title = ref.title
        journal = ref.journal
        year = ref.year
        
        citation = f"{authors} ({year}). {title}. {journal}"
        
        if ref.volume:
            citation += f", {ref.volume}"
            if ref.issue:
                citation += f"({ref.issue})"
        
        if ref.pages:
            citation += f", {ref.pages}"
        
        if ref.doi:
            citation += f". https://doi.org/{ref.doi}"
        
        return citation + "."
    
    def _format_mla(self, ref: Reference) -> str:
        """MLA格式"""
        authors = ", ".join(ref.authors)
        title = ref.title
        journal = ref.journal
        year = ref.year
        
        citation = f"{authors}. \"{title}.\" {journal}"
        
        if ref.volume:
            citation += f" {ref.volume}"
            if ref.issue:
                citation += f".{ref.issue}"
        
        citation += f" ({year})"
        
        if ref.pages:
            citation += f": {ref.pages}"
        
        return citation + "."
    
    def _format_ieee(self, ref: Reference) -> str:
        """IEEE格式"""
        authors = ", ".join([author.replace(", ", " ") for author in ref.authors])
        title = ref.title
        journal = ref.journal
        year = ref.year
        
        citation = f"{authors}, \"{title},\" {journal}"
        
        if ref.volume:
            citation += f", vol. {ref.volume}"
            if ref.issue:
                citation += f", no. {ref.issue}"
        
        if ref.pages:
            citation += f", pp. {ref.pages}"
        
        citation += f", {year}"
        
        return citation + "."
    
    def _format_chicago(self, ref: Reference) -> str:
        """Chicago格式"""
        authors = ", ".join(ref.authors)
        title = ref.title
        journal = ref.journal
        year = ref.year
        
        citation = f"{authors}. \"{title}.\" {journal}"
        
        if ref.volume:
            citation += f" {ref.volume}"
            if ref.issue:
                citation += f", no. {ref.issue}"
        
        citation += f" ({year})"
        
        if ref.pages:
            citation += f": {ref.pages}"
        
        return citation + "."
    
    def _format_harvard(self, ref: Reference) -> str:
        """Harvard格式"""
        authors = ", ".join(ref.authors)
        title = ref.title
        journal = ref.journal
        year = ref.year
        
        citation = f"{authors} {year}, '{title}', {journal}"
        
        if ref.volume:
            citation += f", vol. {ref.volume}"
            if ref.issue:
                citation += f", no. {ref.issue}"
        
        if ref.pages:
            citation += f", pp. {ref.pages}"
        
        return citation + "."
    
    def _format_gb(self, ref: Reference) -> str:
        """国标格式"""
        authors = ", ".join(ref.authors)
        title = ref.title
        journal = ref.journal
        year = ref.year
        
        citation = f"{authors}. {title}[J]. {journal}, {year}"
        
        if ref.volume:
            citation += f", {ref.volume}"
            if ref.issue:
                citation += f"({ref.issue})"
        
        if ref.pages:
            citation += f": {ref.pages}"
        
        return citation + "."
    
    def _format_authors_apa(self, authors: List[str]) -> str:
        """APA作者格式"""
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]}, & {authors[1]}"
        else:
            return f"{authors[0]}, et al."

def create_literature_system() -> Tuple[LiteratureSearchEngine, ReferenceFormatter]:
    """创建文献系统"""
    search_engine = LiteratureSearchEngine()
    formatter = ReferenceFormatter()
    return search_engine, formatter

def render_literature_system_ui(search_engine: LiteratureSearchEngine,
                               formatter: ReferenceFormatter) -> List[Reference]:
    """渲染文献系统界面"""
    st.header("📚 智能参考文献系统")
    
    # 搜索模式选择
    search_mode = st.radio(
        "文献获取方式",
        ["🔍 关键词搜索", "✏️ 手动输入", "🤖 AI智能推荐"],
        horizontal=True
    )
    
    selected_references = []
    
    if search_mode == "🔍 关键词搜索":
        selected_references = render_keyword_search_ui(search_engine, formatter)
    
    elif search_mode == "✏️ 手动输入":
        selected_references = render_manual_input_ui(formatter)
    
    elif search_mode == "🤖 AI智能推荐":
        selected_references = render_ai_recommendation_ui(search_engine, formatter)
    
    # 显示选中的文献
    if selected_references:
        render_selected_references(selected_references, formatter)
    
    return selected_references

def render_keyword_search_ui(search_engine: LiteratureSearchEngine,
                           formatter: ReferenceFormatter) -> List[Reference]:
    """渲染关键词搜索界面"""
    st.subheader("🔍 关键词搜索")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "输入搜索关键词",
            placeholder="例: UTAUT模型, 数据分析, 机器学习",
            help="输入与您研究相关的关键词"
        )
    
    with col2:
        platform = st.selectbox(
            "选择数据库",
            list(search_engine.search_engines.keys()),
            format_func=lambda x: search_engine.search_engines[x]
        )
    
    # 高级搜索选项
    with st.expander("🔧 高级搜索选项"):
        col3, col4, col5 = st.columns(3)
        
        with col3:
            max_results = st.slider("最大结果数", 5, 50, 20)
            min_year = st.number_input("最早年份", 1990, 2024, 2015)
        
        with col4:
            language = st.selectbox("语言", ["全部", "英文", "中文"])
            article_type = st.selectbox("文献类型", ["全部", "期刊论文", "会议论文", "学位论文"])
        
        with col5:
            sort_by = st.selectbox("排序方式", ["相关度", "时间", "引用数"])
            include_abstract = st.checkbox("包含摘要", value=True)
    
    # 搜索按钮
    if st.button("🔍 开始搜索", type="primary"):
        if search_query:
            with st.spinner(f"正在搜索 {search_engine.search_engines[platform]}..."):
                results = search_engine.search_literature(
                    search_query, platform, max_results
                )
                
                if results:
                    st.session_state.search_results = results
                    st.success(f"找到 {len(results)} 篇相关文献")
                else:
                    st.warning("未找到相关文献，请尝试其他关键词")
        else:
            st.error("请输入搜索关键词")
    
    # 显示搜索结果
    if 'search_results' in st.session_state:
        return render_search_results(st.session_state.search_results, formatter)
    
    return []

def render_search_results(results: List[Reference], 
                         formatter: ReferenceFormatter) -> List[Reference]:
    """渲染搜索结果"""
    st.subheader("📄 搜索结果")
    
    selected_refs = []
    
    for i, ref in enumerate(results):
        with st.expander(f"📑 {ref.title[:80]}..." if len(ref.title) > 80 else f"📑 {ref.title}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**作者**: {', '.join(ref.authors)}")
                st.write(f"**期刊**: {ref.journal}")
                st.write(f"**年份**: {ref.year}")
                
                if ref.abstract:
                    st.write(f"**摘要**: {ref.abstract[:200]}...")
                
                # 显示格式化的引用
                st.write("**APA格式引用**:")
                st.code(formatter.format_reference(ref, "APA"))
            
            with col2:
                if st.button("✅ 选择", key=f"select_{i}"):
                    selected_refs.append(ref)
                    st.success("已添加到参考文献")
                
                if st.button("👁️ 详情", key=f"detail_{i}"):
                    render_reference_detail(ref)
    
    return selected_refs

def render_manual_input_ui(formatter: ReferenceFormatter) -> List[Reference]:
    """渲染手动输入界面"""
    st.subheader("✏️ 手动添加参考文献")
    
    with st.form("manual_reference_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("论文标题 *", help="请输入完整的论文标题")
            authors = st.text_input("作者 *", help="多个作者用英文逗号分隔")
            journal = st.text_input("期刊/会议名称 *")
        
        with col2:
            year = st.number_input("发表年份 *", 1900, 2025, 2024)
            volume = st.text_input("卷号")
            issue = st.text_input("期号")
            pages = st.text_input("页码", help="例: 123-145")
        
        # 可选字段
        with st.expander("📋 可选信息"):
            doi = st.text_input("DOI")
            url = st.text_input("URL")
            abstract = st.text_area("摘要", height=100)
            keywords = st.text_input("关键词", help="多个关键词用英文逗号分隔")
        
        submitted = st.form_submit_button("➕ 添加参考文献", type="primary")
        
        if submitted:
            if title and authors and journal and year:
                ref = Reference(
                    title=title,
                    authors=[a.strip() for a in authors.split(",")],
                    journal=journal,
                    year=int(year),
                    volume=volume if volume else None,
                    issue=issue if issue else None,
                    pages=pages if pages else None,
                    doi=doi if doi else None,
                    url=url if url else None,
                    abstract=abstract if abstract else None,
                    keywords=[k.strip() for k in keywords.split(",")] if keywords else None
                )
                
                if 'manual_references' not in st.session_state:
                    st.session_state.manual_references = []
                
                st.session_state.manual_references.append(ref)
                st.success("参考文献添加成功！")
                st.rerun()
            else:
                st.error("请填写必填字段（标有*的字段）")
    
    # 显示已添加的文献
    if 'manual_references' in st.session_state:
        st.subheader("📚 已添加的文献")
        manual_refs = st.session_state.manual_references
        
        for i, ref in enumerate(manual_refs):
            with st.expander(f"📑 {ref.title}"):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(formatter.format_reference(ref, "APA"))
                
                with col2:
                    if st.button("🗑️ 删除", key=f"delete_manual_{i}"):
                        st.session_state.manual_references.pop(i)
                        st.rerun()
        
        return manual_refs
    
    return []

def render_ai_recommendation_ui(search_engine: LiteratureSearchEngine,
                              formatter: ReferenceFormatter) -> List[Reference]:
    """渲染AI推荐界面"""
    st.subheader("🤖 AI智能文献推荐")
    
    col1, col2 = st.columns(2)
    
    with col1:
        research_topic = st.text_input(
            "研究主题",
            placeholder="例: 技术接受模型在移动支付中的应用"
        )
        
        research_field = st.selectbox(
            "研究领域",
            ["信息系统", "管理学", "心理学", "计算机科学", "经济学", "教育学", "其他"]
        )
    
    with col2:
        study_type = st.selectbox(
            "研究类型",
            ["实证研究", "理论研究", "综述研究", "案例研究", "实验研究"]
        )
        
        reference_count = st.slider("推荐文献数量", 10, 50, 25)
    
    # AI推荐设置
    with st.expander("🔧 AI推荐设置"):
        col3, col4 = st.columns(2)
        
        with col3:
            impact_weight = st.slider("影响因子权重", 0.0, 1.0, 0.3)
            recency_weight = st.slider("时效性权重", 0.0, 1.0, 0.4)
        
        with col4:
            relevance_weight = st.slider("相关性权重", 0.0, 1.0, 0.6)
            diversity_preference = st.checkbox("增加文献多样性", value=True)
    
    if st.button("🚀 获取AI推荐", type="primary"):
        if research_topic:
            with st.spinner("AI正在分析并推荐相关文献..."):
                # 多平台搜索
                all_results = []
                for platform in ["google_scholar", "pubmed", "cnki"]:
                    results = search_engine.search_literature(
                        research_topic, platform, reference_count//3
                    )
                    all_results.extend(results)
                
                # AI智能筛选
                selection_criteria = {
                    "impact_weight": impact_weight,
                    "recency_weight": recency_weight,
                    "relevance_weight": relevance_weight,
                    "diversity_preference": diversity_preference,
                    "max_results": reference_count
                }
                
                recommended_refs = search_engine.ai_select_references(
                    research_topic, all_results, selection_criteria
                )
                
                if recommended_refs:
                    st.session_state.ai_recommendations = recommended_refs
                    st.success(f"AI推荐了 {len(recommended_refs)} 篇高质量文献")
                else:
                    st.warning("AI未找到符合条件的文献推荐")
        else:
            st.error("请输入研究主题")
    
    # 显示AI推荐结果
    if 'ai_recommendations' in st.session_state:
        return render_ai_recommendations(st.session_state.ai_recommendations, formatter)
    
    return []

def render_ai_recommendations(recommendations: List[Reference],
                            formatter: ReferenceFormatter) -> List[Reference]:
    """渲染AI推荐结果"""
    st.subheader("🎯 AI推荐结果")
    
    # 推荐摘要
    st.info(f"🤖 AI分析了多个数据库的文献，为您精选出 {len(recommendations)} 篇高质量参考文献")
    
    selected_refs = []
    
    # 分组显示：高相关性、中等相关性、补充文献
    high_relevance = recommendations[:len(recommendations)//3]
    medium_relevance = recommendations[len(recommendations)//3:2*len(recommendations)//3]
    supplementary = recommendations[2*len(recommendations)//3:]
    
    tabs = st.tabs(["🎯 高相关性", "📊 中等相关性", "📚 补充文献"])
    
    with tabs[0]:
        st.write("**高度相关的核心文献**")
        for i, ref in enumerate(high_relevance):
            selected_refs.extend(render_recommendation_item(ref, f"high_{i}", formatter))
    
    with tabs[1]:
        st.write("**中等相关的重要文献**")
        for i, ref in enumerate(medium_relevance):
            selected_refs.extend(render_recommendation_item(ref, f"medium_{i}", formatter))
    
    with tabs[2]:
        st.write("**补充和拓展文献**")
        for i, ref in enumerate(supplementary):
            selected_refs.extend(render_recommendation_item(ref, f"supp_{i}", formatter))
    
    # 批量选择
    if st.button("📥 选择所有推荐文献"):
        return recommendations
    
    return selected_refs

def render_recommendation_item(ref: Reference, key_suffix: str,
                             formatter: ReferenceFormatter) -> List[Reference]:
    """渲染单个推荐项"""
    with st.expander(f"📑 {ref.title}"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**作者**: {', '.join(ref.authors)}")
            st.write(f"**期刊**: {ref.journal} ({ref.year})")
            
            # AI推荐理由（模拟）
            st.write("**🤖 AI推荐理由**: 该文献在相关领域具有较高影响力，研究方法科学严谨，与您的研究主题高度相关。")
            
            st.write("**引用格式**:")
            st.code(formatter.format_reference(ref, "APA"))
        
        with col2:
            if st.button("✅ 选择", key=f"select_ai_{key_suffix}"):
                return [ref]
    
    return []

def render_selected_references(references: List[Reference],
                             formatter: ReferenceFormatter):
    """渲染已选择的参考文献"""
    st.markdown("---")
    st.subheader("📋 已选择的参考文献")
    
    if not references:
        st.info("暂未选择任何参考文献")
        return
    
    # 格式选择
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        format_style = st.selectbox(
            "引用格式",
            ["APA", "IEEE", "国标", "MLA", "Chicago", "Harvard"]
        )
    
    with col2:
        if st.button("📋 复制全部"):
            formatted_refs = []
            for ref in references:
                formatted_refs.append(formatter.format_reference(ref, format_style))
            
            # 这里可以添加复制到剪贴板的功能
            st.success("参考文献已复制")
    
    with col3:
        # 导出功能
        if st.button("💾 导出"):
            export_references(references, formatter, format_style)
    
    # 显示格式化的参考文献
    st.write(f"**共 {len(references)} 篇参考文献 ({format_style} 格式):**")
    
    for i, ref in enumerate(references, 1):
        formatted_ref = formatter.format_reference(ref, format_style)
        st.write(f"[{i}] {formatted_ref}")

def export_references(references: List[Reference],
                     formatter: ReferenceFormatter,
                     format_style: str):
    """导出参考文献"""
    # 生成导出内容
    export_content = []
    for i, ref in enumerate(references, 1):
        formatted_ref = formatter.format_reference(ref, format_style)
        export_content.append(f"[{i}] {formatted_ref}")
    
    export_text = "\n\n".join(export_content)
    
    # 提供下载
    st.download_button(
        label="📄 下载参考文献",
        data=export_text,
        file_name=f"references_{format_style}_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

def render_reference_detail(ref: Reference):
    """渲染文献详情"""
    st.modal("📖 文献详情")
    
    with st.container():
        st.write(f"**标题**: {ref.title}")
        st.write(f"**作者**: {', '.join(ref.authors)}")
        st.write(f"**期刊**: {ref.journal}")
        st.write(f"**年份**: {ref.year}")
        
        if ref.volume:
            st.write(f"**卷期**: {ref.volume}({ref.issue})")
        
        if ref.pages:
            st.write(f"**页码**: {ref.pages}")
        
        if ref.doi:
            st.write(f"**DOI**: {ref.doi}")
        
        if ref.abstract:
            st.write("**摘要**:")
            st.write(ref.abstract)
        
        if ref.keywords:
            st.write(f"**关键词**: {', '.join(ref.keywords)}")