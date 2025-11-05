import os
import re
import json
import logging
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAssistant:
    """
    AI智能助手类，用于提供数据分析报告撰写辅助功能
    """
    
    def __init__(self):
        """
        初始化AI智能助手
        """
        self.knowledge_base = {
            'statistical_terms': self._load_statistical_terms(),
            'data_analysis_patterns': self._load_analysis_patterns(),
            'report_templates': self._load_report_templates()
        }
        self.context_memory = []
        
    def _load_statistical_terms(self) -> Dict[str, str]:
        """
        加载统计学术语库
        """
        return {
            '描述性统计': '描述性统计是通过图表或数学方法，对数据资料进行整理、分析，并对数据的分布状态、数字特征和随机变量之间关系进行估计和描述的方法。',
            '相关性分析': '相关性分析是研究两个或多个变量之间相关程度的一种统计方法，通常用相关系数来表示变量间相关的密切程度和方向。',
            '回归分析': '回归分析是确定两种或两种以上变量间相互依赖的定量关系的一种统计分析方法，主要用于预测和因果关系研究。',
            '假设检验': '假设检验是用来判断样本与样本、样本与总体的差异是由抽样误差引起还是本质差别造成的统计推断方法。',
            '置信区间': '置信区间是指由样本统计量所构造的总体参数的估计区间，它表示这个区间以一定的概率包含总体参数的真值。'
        }
    
    def _load_analysis_patterns(self) -> List[Dict[str, Any]]:
        """
        加载数据分析模式库
        """
        return [
            {
                'name': '趋势分析',
                'description': '分析数据随时间变化的趋势和规律',
                'keywords': ['趋势', '时间序列', '变化', '增长', '下降'],
                'chart_types': ['折线图', '面积图']
            },
            {
                'name': '分布分析',
                'description': '分析数据的分布特征和分布规律',
                'keywords': ['分布', '频率', '直方图', '正态分布'],
                'chart_types': ['直方图', '箱线图', '饼图']
            },
            {
                'name': '关联分析',
                'description': '分析变量之间的关联性和相互影响',
                'keywords': ['关联', '相关', '关系', '影响', '依赖'],
                'chart_types': ['散点图', '热力图', '相关性矩阵']
            },
            {
                'name': '对比分析',
                'description': '对比不同类别或不同时期的数据差异',
                'keywords': ['对比', '比较', '差异', '占比', '比例'],
                'chart_types': ['柱状图', '雷达图']
            }
        ]
    
    def _load_report_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        加载报告模板
        """
        return {
            'summary_template': {
                'title': '数据分析总结',
                'structure': [
                    '数据概况：',
                    '主要发现：',
                    '业务洞察：',
                    '建议行动：'
                ]
            },
            'detailed_analysis_template': {
                'title': '详细分析报告',
                'structure': [
                    '1. 项目背景和目标',
                    '2. 数据描述和预处理',
                    '3. 数据分析方法',
                    '4. 分析结果',
                    '5. 结论和建议',
                    '6. 附录'
                ]
            }
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        分析用户查询，识别意图和需求
        
        Args:
            query: 用户的查询文本
            
        Returns:
            包含查询分析结果的字典
        """
        try:
            query_lower = query.lower()
            intent = {
                'type': 'unknown',
                'keywords': [],
                'data_related': False
            }
            
            # 识别查询类型
            if any(keyword in query_lower for keyword in ['解释', '什么是', '什么叫做', '定义']):
                intent['type'] = 'explanation'
            elif any(keyword in query_lower for keyword in ['建议', '推荐', '如何']):
                intent['type'] = 'recommendation'
            elif any(keyword in query_lower for keyword in ['总结', '分析', '报告']):
                intent['type'] = 'summary'
            elif any(keyword in query_lower for keyword in ['图表', '可视化', '展示']):
                intent['type'] = 'visualization'
            
            # 提取关键词
            for pattern in self.knowledge_base['data_analysis_patterns']:
                for keyword in pattern['keywords']:
                    if keyword in query_lower:
                        intent['keywords'].append(keyword)
            
            # 判断是否与数据相关
            intent['data_related'] = len(intent['keywords']) > 0
            
            logger.info(f"查询分析结果: {intent}")
            return intent
        except Exception as e:
            logger.error(f"查询分析失败: {str(e)}")
            return {'type': 'unknown', 'keywords': [], 'data_related': False}
    
    def generate_response(self, query: str, data: Optional[pd.DataFrame] = None, analysis_results: Optional[Dict] = None) -> str:
        """
        根据用户查询和上下文生成智能响应
        
        Args:
            query: 用户的查询文本
            data: 可选的DataFrame数据
            analysis_results: 可选的分析结果字典
            
        Returns:
            生成的响应文本
        """
        try:
            # 分析查询
            intent = self.analyze_query(query)
            
            # 根据不同的查询类型生成响应
            if intent['type'] == 'explanation':
                return self._generate_explanation_response(query)
            elif intent['type'] == 'recommendation':
                return self._generate_recommendation_response(query, data, analysis_results)
            elif intent['type'] == 'summary':
                return self._generate_summary_response(data, analysis_results)
            elif intent['type'] == 'visualization':
                return self._generate_visualization_response(query, data)
            else:
                return self._generate_general_response(query)
        except Exception as e:
            logger.error(f"生成响应失败: {str(e)}")
            return "抱歉，我在处理您的请求时遇到了问题。请尝试用不同的方式提问。"
    
    def _generate_explanation_response(self, query: str) -> str:
        """
        生成解释性响应
        """
        query_lower = query.lower()
        
        # 查找统计学术语解释
        for term, explanation in self.knowledge_base['statistical_terms'].items():
            if term.lower() in query_lower:
                return f"**{term}**的解释：{explanation}"
        
        # 查找分析模式解释
        for pattern in self.knowledge_base['data_analysis_patterns']:
            if any(keyword in query_lower for keyword in pattern['keywords']):
                return f"**{pattern['name']}**是{pattern['description']}。适合使用的图表类型包括：{', '.join(pattern['chart_types'])}"
        
        return "我理解您需要解释，但我可能没有这方面的专业知识。请尝试提供更具体的术语或概念。"
    
    def _generate_recommendation_response(self, query: str, data: Optional[pd.DataFrame] = None, analysis_results: Optional[Dict] = None) -> str:
        """
        生成推荐性响应
        """
        if data is None:
            return "为了给您提供准确的建议，请先上传并分析您的数据。"
        
        recommendations = []
        
        # 数据特征分析
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        if len(numeric_cols) > 0:
            recommendations.append(f"您的数据包含{len(numeric_cols)}个数值型特征，适合进行统计分析和可视化。")
        
        if len(categorical_cols) > 0:
            recommendations.append(f"您的数据包含{len(categorical_cols)}个类别型特征，可以进行分组分析和交叉分析。")
        
        # 提供分析建议
        if '趋势' in query.lower() and '时间' in data.columns:
            recommendations.append("建议您进行时间序列分析，查看数据随时间变化的趋势。")
        elif '分布' in query.lower():
            recommendations.append("建议您查看数据的分布情况，识别异常值和数据特征。")
        elif '相关' in query.lower() and len(numeric_cols) > 1:
            recommendations.append("建议您进行相关性分析，探索变量之间的关系。")
        
        # 图表类型推荐
        chart_recommendations = self._recommend_chart_types(data)
        if chart_recommendations:
            recommendations.append(f"根据您的数据特征，推荐的图表类型包括：{', '.join(chart_recommendations)}")
        
        if not recommendations:
            recommendations.append("根据您的数据，建议您先进行基础的描述性统计分析，了解数据的基本特征。")
        
        return "\n".join(recommendations)
    
    def _generate_summary_response(self, data: Optional[pd.DataFrame] = None, analysis_results: Optional[Dict] = None) -> str:
        """
        生成总结性响应
        """
        if data is None:
            return "请先上传并分析数据，我可以帮您生成数据分析总结。"
        
        summary = "# 数据分析总结\n\n"
        
        # 数据概况
        summary += "## 数据概况\n"
        summary += f"- 数据规模：{len(data)}行 × {len(data.columns)}列\n"
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        summary += f"- 数值型特征：{len(numeric_cols)}个\n"
        summary += f"- 类别型特征：{len(categorical_cols)}个\n\n"
        
        # 基本统计信息
        if len(numeric_cols) > 0:
            summary += "## 数值特征统计\n"
            # 选择前3个数值列展示基本统计信息
            top_numeric_cols = numeric_cols[:3]
            for col in top_numeric_cols:
                col_stats = data[col].describe()
                summary += f"### {col}\n"
                summary += f"- 平均值：{col_stats['mean']:.2f}\n"
                summary += f"- 中位数：{col_stats['50%']:.2f}\n"
                summary += f"- 标准差：{col_stats['std']:.2f}\n"
                summary += f"- 最小值：{col_stats['min']:.2f}\n"
                summary += f"- 最大值：{col_stats['max']:.2f}\n\n"
        
        # 建议行动
        summary += "## 建议行动\n"
        summary += "1. 根据数据特征，选择合适的分析方法和可视化图表\n"
        summary += "2. 关注数据中的异常值和缺失值，必要时进行数据清洗\n"
        summary += "3. 深入分析变量之间的关系，挖掘业务洞察\n"
        summary += "4. 基于分析结果，制定具体的业务决策和行动计划\n"
        
        return summary
    
    def _generate_visualization_response(self, query: str, data: Optional[pd.DataFrame] = None) -> str:
        """
        生成可视化相关响应
        """
        if data is None:
            return "请先上传数据，我可以帮您推荐合适的可视化方案。"
        
        query_lower = query.lower()
        recommendations = []
        
        # 推荐图表类型
        chart_recommendations = self._recommend_chart_types(data)
        if chart_recommendations:
            recommendations.append(f"为您的数据推荐的图表类型：{', '.join(chart_recommendations)}")
        
        # 根据关键词提供更具体的建议
        if any(keyword in query_lower for keyword in ['趋势', '时间序列']):
            if '时间' in data.columns:
                recommendations.append("建议使用折线图展示时间趋势数据，便于观察变化规律。")
            else:
                recommendations.append("您的数据中可能没有明显的时间列。请检查是否需要进行时间序列分析。")
        elif any(keyword in query_lower for keyword in ['分布', '频率']):
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                recommendations.append(f"建议使用直方图或箱线图展示{', '.join(numeric_cols[:3])}等数值列的分布情况。")
        elif any(keyword in query_lower for keyword in ['对比', '比较']):
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                recommendations.append(f"建议使用柱状图对比{categorical_cols[0]}不同类别的数据。")
        
        # 可视化最佳实践
        recommendations.append("\n可视化最佳实践：")
        recommendations.append("1. 确保图表标题清晰，突出重点")
        recommendations.append("2. 使用合适的颜色方案，提高可读性")
        recommendations.append("3. 添加坐标轴标签和图例")
        recommendations.append("4. 避免图表过于复杂，突出关键信息")
        
        return "\n".join(recommendations)
    
    def _generate_general_response(self, query: str) -> str:
        """
        生成通用响应
        """
        general_responses = [
            "您好！我是数据分析助手，可以帮您解释统计概念、推荐分析方法、生成分析总结和可视化建议。",
            "请告诉我您需要哪方面的数据分析帮助？例如：解释统计概念、推荐分析方法、生成分析总结等。",
            "我可以帮助您理解数据、选择合适的分析方法、推荐可视化图表，并生成专业的分析报告。"
        ]
        
        # 简单的响应选择逻辑
        if any(keyword in query.lower() for keyword in ['你好', '嗨', '您好']):
            return general_responses[0]
        elif any(keyword in query.lower() for keyword in ['帮助', '使用', '怎么用']):
            return general_responses[1]
        else:
            return general_responses[2]
    
    def _recommend_chart_types(self, data: pd.DataFrame) -> List[str]:
        """
        根据数据特征推荐合适的图表类型
        """
        recommendations = []
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        # 基于数据特征推荐图表
        if len(numeric_cols) > 0:
            recommendations.append("直方图")  # 展示数值分布
            recommendations.append("箱线图")  # 展示异常值和分布
            
            if len(numeric_cols) >= 2:
                recommendations.append("散点图")  # 展示变量关系
        
        if len(categorical_cols) > 0:
            recommendations.append("柱状图")  # 展示类别对比
            recommendations.append("饼图")    # 展示占比关系
        
        # 检查是否有时间相关列
        time_keywords = ['时间', '日期', 'date', 'time', 'year', 'month', 'day']
        if any(any(keyword in col.lower() for keyword in time_keywords) for col in data.columns):
            recommendations.append("折线图")  # 展示时间趋势
        
        # 去重并限制数量
        return list(set(recommendations))[:5]
    
    def generate_report_section(self, section_type: str, data: Optional[pd.DataFrame] = None, analysis_results: Optional[Dict] = None) -> str:
        """
        生成报告的特定部分
        
        Args:
            section_type: 报告部分类型
            data: 可选的DataFrame数据
            analysis_results: 可选的分析结果字典
            
        Returns:
            生成的报告部分内容
        """
        if section_type == 'data_overview' and data is not None:
            return self._generate_data_overview(data)
        elif section_type == 'key_findings' and analysis_results is not None:
            return self._generate_key_findings(analysis_results)
        elif section_type == 'business_insights':
            return self._generate_business_insights(data, analysis_results)
        elif section_type == 'recommendations':
            return self._generate_recommendations(data, analysis_results)
        else:
            return "无法生成指定类型的报告部分。请提供有效的部分类型和相关数据。"
    
    def _generate_data_overview(self, data: pd.DataFrame) -> str:
        """
        生成数据概况部分
        """
        overview = "## 1. 数据概况\n\n"
        overview += f"数据包含 **{len(data)} 行** 和 **{len(data.columns)} 列**。\n\n"
        
        # 数据类型统计
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        overview += "### 1.1 数据类型分布\n"
        overview += f"- 数值型特征：**{len(numeric_cols)}** 个\n"
        overview += f"- 类别型特征：**{len(categorical_cols)}** 个\n\n"
        
        # 缺失值统计
        missing_count = data.isnull().sum().sum()
        if missing_count > 0:
            overview += "### 1.2 缺失值情况\n"
            overview += f"数据中共有 **{missing_count}** 个缺失值。\n"
            
            # 显示缺失值较多的列
            cols_with_missing = data.isnull().sum()
            cols_with_missing = cols_with_missing[cols_with_missing > 0]
            if not cols_with_missing.empty:
                overview += "缺失值较多的列：\n"
                for col, count in cols_with_missing.head(5).items():
                    missing_pct = (count / len(data)) * 100
                    overview += f"  - {col}: {count} 个 ({missing_pct:.1f}%)\n"
            overview += "\n"
        
        # 显示部分数据列信息
        overview += "### 1.3 主要数据列\n"
        
        # 数值列统计信息
        if len(numeric_cols) > 0:
            overview += "#### 数值型特征\n"
            for col in numeric_cols[:3]:
                stats = data[col].describe()
                overview += f"- **{col}**: 平均值 {stats['mean']:.2f}, 范围 [{stats['min']:.2f}, {stats['max']:.2f}]\n"
        
        # 类别列信息
        if len(categorical_cols) > 0:
            overview += "#### 类别型特征\n"
            for col in categorical_cols[:3]:
                unique_count = data[col].nunique()
                overview += f"- **{col}**: {unique_count} 个不同类别\n"
        
        return overview
    
    def _generate_key_findings(self, analysis_results: Dict) -> str:
        """
        生成关键发现部分
        """
        findings = "## 2. 关键发现\n\n"
        
        # 从分析结果中提取关键发现
        if 'correlation_results' in analysis_results and analysis_results['correlation_results']:
            findings += "### 2.1 相关性发现\n"
            for result in analysis_results['correlation_results'][:3]:
                findings += f"- **强相关性**: {result['feature1']} 和 {result['feature2']} 之间的相关系数为 {result['correlation']:.3f}\n"
            findings += "\n"
        
        if 'distribution_results' in analysis_results and analysis_results['distribution_results']:
            findings += "### 2.2 分布特征\n"
            for result in analysis_results['distribution_results'][:3]:
                findings += f"- **{result['feature']}**: {result['description']}\n"
            findings += "\n"
        
        if 'outlier_results' in analysis_results and analysis_results['outlier_results']:
            findings += "### 2.3 异常值发现\n"
            findings += f"数据中检测到 **{analysis_results['outlier_results']['count']}** 个异常值。\n"
            findings += f"异常值主要集中在：{', '.join(analysis_results['outlier_results']['features'][:3])} 等特征中。\n\n"
        
        if not any(key in analysis_results for key in ['correlation_results', 'distribution_results', 'outlier_results']):
            findings += "基于当前分析，尚未发现显著的统计特征。建议进行更深入的分析。\n"
        
        return findings
    
    def _generate_business_insights(self, data: Optional[pd.DataFrame] = None, analysis_results: Optional[Dict] = None) -> str:
        """
        生成业务洞察部分
        """
        insights = "## 3. 业务洞察\n\n"
        
        # 通用业务洞察
        insights += "### 3.1 数据驱动的业务理解\n"
        insights += "- 数据分析结果揭示了业务运营中的关键模式和规律\n"
        insights += "- 通过量化分析，可以更客观地评估业务表现\n"
        insights += "- 数据中的异常值可能指示业务流程中的问题或机会\n\n"
        
        # 如果有分析结果，可以提供更具体的洞察
        if analysis_results:
            insights += "### 3.2 具体业务启示\n"
            if 'correlation_results' in analysis_results:
                insights += "- 强相关的变量可能暗示因果关系，值得进一步调查\n"
            if 'distribution_results' in analysis_results:
                insights += "- 数据分布特征反映了客户行为或市场规律\n"
        
        insights += "\n### 3.3 数据质量评估\n"
        insights += "- 数据完整性和准确性对业务决策至关重要\n"
        insights += "- 建议定期评估数据质量，确保分析结果的可靠性\n"
        
        return insights
    
    def _generate_recommendations(self, data: Optional[pd.DataFrame] = None, analysis_results: Optional[Dict] = None) -> str:
        """
        生成建议部分
        """
        recommendations = "## 4. 行动建议\n\n"
        
        # 分析建议
        recommendations += "### 4.1 深入分析方向\n"
        recommendations += "- 进行更细粒度的数据分析，识别细分市场或用户群体\n"
        recommendations += "- 开展时间序列分析，了解业务指标的变化趋势\n"
        recommendations += "- 进行预测建模，为未来业务发展提供预测支持\n\n"
        
        # 业务建议
        recommendations += "### 4.2 业务优化建议\n"
        recommendations += "- 基于数据分析结果，优化业务流程和资源分配\n"
        recommendations += "- 针对发现的问题和机会，制定具体的改进措施\n"
        recommendations += "- 建立数据驱动的决策机制，定期评估业务表现\n\n"
        
        # 数据管理建议
        recommendations += "### 4.3 数据管理建议\n"
        recommendations += "- 建立完善的数据收集和管理流程\n"
        recommendations += "- 定期更新数据分析模型，适应业务变化\n"
        recommendations += "- 提升团队数据分析能力，培养数据驱动文化\n"
        
        return recommendations
    
    def save_conversation(self, conversation: List[Dict[str, str]], file_path: str) -> bool:
        """
        保存对话历史
        
        Args:
            conversation: 对话历史列表
            file_path: 保存文件路径
            
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存对话历史
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)
            
            logger.info(f"对话历史已保存到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存对话历史失败: {str(e)}")
            return False

def create_ai_assistant() -> AIAssistant:
    """
    创建AI助手实例
    
    Returns:
        AIAssistant实例
    """
    return AIAssistant()

# 示例使用
if __name__ == "__main__":
    # 创建AI助手
    assistant = create_ai_assistant()
    
    # 示例响应
    print(assistant.generate_response("你好，我需要数据分析帮助"))
    print("\n" + "="*50 + "\n")
    print(assistant.generate_response("什么是相关性分析？"))