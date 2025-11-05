# AI报告增强模块
import openai
import requests
import json
import logging
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np
from datetime import datetime
import os
from dataclasses import dataclass

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class AIModelConfig:
    """AI模型配置类"""
    provider: str  # 'openai', 'claude', 'qwen', 'chatglm', 'local'
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30

class AIReportEnhancer:
    """
    AI大模型报告增强器
    用于在生成报告前对分析结果进行智能优化和内容增强
    """
    
    def __init__(self, config: AIModelConfig):
        """
        初始化AI报告增强器
        
        Args:
            config: AI模型配置
        """
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化AI客户端"""
        try:
            if self.config.provider == 'openai':
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.api_base if self.config.api_base else None
                )
                logger.info("OpenAI客户端初始化成功")
                
            elif self.config.provider == 'qwen':
                # 通义千问API配置
                self.headers = {
                    'Authorization': f'Bearer {self.config.api_key}',
                    'Content-Type': 'application/json'
                }
                self.api_url = self.config.api_base or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                logger.info("通义千问客户端初始化成功")
                
            elif self.config.provider == 'chatglm':
                # ChatGLM API配置
                self.headers = {
                    'Authorization': f'Bearer {self.config.api_key}',
                    'Content-Type': 'application/json'
                }
                self.api_url = self.config.api_base or "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                logger.info("ChatGLM客户端初始化成功")
                
            elif self.config.provider == 'local':
                # 本地模型API（如Ollama）
                self.api_url = self.config.api_base or "http://localhost:11434/api/generate"
                logger.info("本地模型客户端初始化成功")
                
        except Exception as e:
            logger.error(f"AI客户端初始化失败: {str(e)}")
            raise
    
    def enhance_analysis_results(self, 
                                data: pd.DataFrame,
                                analysis_results: Dict,
                                enhancement_type: str = "comprehensive") -> Dict:
        """
        使用AI大模型增强分析结果
        
        Args:
            data: 原始数据
            analysis_results: 原始分析结果
            enhancement_type: 增强类型 ("comprehensive", "insights", "recommendations", "interpretation")
            
        Returns:
            增强后的分析结果
        """
        try:
            logger.info(f"开始AI增强分析结果，类型: {enhancement_type}")
            
            # 准备数据摘要
            data_summary = self._prepare_data_summary(data)
            
            # 准备分析结果摘要
            results_summary = self._prepare_results_summary(analysis_results)
            
            # 构建增强提示
            prompt = self._build_enhancement_prompt(
                data_summary, 
                results_summary, 
                enhancement_type
            )
            
            # 调用AI模型
            enhanced_content = self._call_ai_model(prompt)
            
            # 解析AI响应并整合到原结果中
            enhanced_results = self._integrate_ai_response(
                analysis_results, 
                enhanced_content, 
                enhancement_type
            )
            
            logger.info("AI增强分析结果完成")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"AI增强分析结果失败: {str(e)}")
            # 如果AI增强失败，返回原始结果
            return analysis_results
    
    def _prepare_data_summary(self, data: pd.DataFrame) -> Dict:
        """准备数据摘要信息"""
        try:
            summary = {
                "shape": data.shape,
                "columns": list(data.columns),
                "dtypes": data.dtypes.to_dict(),
                "missing_values": data.isnull().sum().to_dict(),
                "basic_stats": {}
            }
            
            # 数值型变量统计
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary["basic_stats"]["numeric"] = data[numeric_cols].describe().to_dict()
            
            # 分类型变量统计
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                cat_summary = {}
                for col in categorical_cols[:10]:  # 限制数量避免过长
                    cat_summary[col] = data[col].value_counts().head().to_dict()
                summary["basic_stats"]["categorical"] = cat_summary
            
            return summary
            
        except Exception as e:
            logger.error(f"准备数据摘要失败: {str(e)}")
            return {"error": str(e)}
    
    def _prepare_results_summary(self, analysis_results: Dict) -> Dict:
        """准备分析结果摘要"""
        try:
            summary = {}
            
            for key, value in analysis_results.items():
                if isinstance(value, dict):
                    # 提取关键指标
                    if 'test_statistic' in value:
                        summary[key] = {
                            "test_statistic": value.get('test_statistic'),
                            "p_value": value.get('p_value'),
                            "effect_size": value.get('effect_size'),
                            "interpretation": value.get('interpretation', '')
                        }
                    elif 'correlation_matrix' in value:
                        summary[key] = {
                            "type": "correlation_analysis",
                            "significant_correlations": value.get('significant_correlations', []),
                            "strong_correlations": value.get('strong_correlations', [])
                        }
                    elif 'model_performance' in value:
                        summary[key] = {
                            "type": "machine_learning",
                            "best_model": value.get('best_model'),
                            "performance": value.get('model_performance')
                        }
                    else:
                        summary[key] = {"type": "analysis", "summary": str(value)[:200]}
                else:
                    summary[key] = {"type": "simple", "value": str(value)[:100]}
            
            return summary
            
        except Exception as e:
            logger.error(f"准备分析结果摘要失败: {str(e)}")
            return {"error": str(e)}
    
    def _build_enhancement_prompt(self, 
                                data_summary: Dict, 
                                results_summary: Dict, 
                                enhancement_type: str) -> str:
        """构建AI增强提示"""
        
        base_context = f"""
作为专业的数据分析专家，请基于以下数据和分析结果，提供深入的洞察和专业建议。

## 数据概况
- 数据维度: {data_summary.get('shape', 'unknown')}
- 变量类型: {len(data_summary.get('columns', []))} 个变量
- 缺失值情况: {sum(data_summary.get('missing_values', {}).values())} 个缺失值

## 分析结果摘要
{json.dumps(results_summary, ensure_ascii=False, indent=2)}
"""
        
        if enhancement_type == "comprehensive":
            prompt = base_context + """
请提供以下内容：

1. **关键发现总结**: 用简洁的语言总结最重要的3-5个发现
2. **深层洞察**: 分析数据背后的潜在模式和趋势
3. **实际意义**: 解释这些发现对业务或实践的意义
4. **建议措施**: 基于分析结果提出3-5条具体的行动建议
5. **局限性说明**: 指出分析的局限性和需要注意的问题

请用专业但易懂的语言回答，每个部分都要有具体的数据支撑。
"""
        
        elif enhancement_type == "insights":
            prompt = base_context + """
请专注于数据洞察，提供：

1. **异常模式识别**: 识别数据中的异常或意外模式
2. **关联性分析**: 揭示变量间的深层关联
3. **趋势解读**: 解释观察到的趋势及其可能原因
4. **影响因素**: 识别关键影响因素及其作用机制

要求答案具有洞察性和前瞻性。
"""
        
        elif enhancement_type == "recommendations":
            prompt = base_context + """
请专注于提供行动建议：

1. **短期建议**: 基于当前数据可以立即采取的措施
2. **中期策略**: 需要一定时间实施的改进方案
3. **长期规划**: 战略性的发展建议
4. **风险提示**: 需要注意的潜在风险和应对措施

建议要具体、可操作、有优先级。
"""
        
        elif enhancement_type == "interpretation":
            prompt = base_context + """
请专注于结果解释：

1. **统计意义解释**: 用通俗语言解释统计结果的含义
2. **实际意义阐述**: 说明结果在现实中的意义
3. **因果关系分析**: 探讨可能的因果关系（注意区分相关与因果）
4. **置信度评估**: 评估结论的可信度和适用范围

解释要准确、清晰、避免过度解读。
"""
        
        return prompt
    
    def _call_ai_model(self, prompt: str) -> str:
        """调用AI模型获取响应"""
        try:
            if self.config.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": "你是一位专业的数据分析专家，具有丰富的统计学和业务理解能力。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    timeout=self.config.timeout
                )
                return response.choices[0].message.content
                
            elif self.config.provider == 'qwen':
                data = {
                    "model": self.config.model_name,
                    "input": {
                        "messages": [
                            {"role": "system", "content": "你是一位专业的数据分析专家，具有丰富的统计学和业务理解能力。"},
                            {"role": "user", "content": prompt}
                        ]
                    },
                    "parameters": {
                        "max_tokens": self.config.max_tokens,
                        "temperature": self.config.temperature
                    }
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=data,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                result = response.json()
                return result['output']['text']
                
            elif self.config.provider == 'chatglm':
                data = {
                    "model": self.config.model_name,
                    "messages": [
                        {"role": "system", "content": "你是一位专业的数据分析专家，具有丰富的统计学和业务理解能力。"},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=data,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
                
            elif self.config.provider == 'local':
                data = {
                    "model": self.config.model_name,
                    "prompt": f"你是一位专业的数据分析专家。{prompt}",
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens
                    }
                }
                
                response = requests.post(
                    self.api_url,
                    json=data,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                result = response.json()
                return result['response']
                
        except Exception as e:
            logger.error(f"调用AI模型失败: {str(e)}")
            raise
    
    def _integrate_ai_response(self, 
                              original_results: Dict, 
                              ai_response: str, 
                              enhancement_type: str) -> Dict:
        """将AI响应整合到原始结果中"""
        try:
            enhanced_results = original_results.copy()
            
            # 添加AI增强内容
            ai_enhancement = {
                "ai_enhanced": True,
                "enhancement_type": enhancement_type,
                "enhancement_timestamp": datetime.now().isoformat(),
                "ai_provider": self.config.provider,
                "ai_model": self.config.model_name,
                "enhanced_content": ai_response
            }
            
            # 根据增强类型添加到相应位置
            if enhancement_type == "comprehensive":
                enhanced_results["ai_comprehensive_analysis"] = ai_enhancement
            elif enhancement_type == "insights":
                enhanced_results["ai_insights"] = ai_enhancement
            elif enhancement_type == "recommendations":
                enhanced_results["ai_recommendations"] = ai_enhancement
            elif enhancement_type == "interpretation":
                enhanced_results["ai_interpretation"] = ai_enhancement
            
            # 添加增强标记到所有子结果
            for key in enhanced_results:
                if isinstance(enhanced_results[key], dict):
                    enhanced_results[key]["has_ai_enhancement"] = True
            
            logger.info(f"AI响应成功整合，增强类型: {enhancement_type}")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"整合AI响应失败: {str(e)}")
            return original_results

def create_ai_enhancer(provider: str = "openai", 
                      model_name: str = "gpt-3.5-turbo",
                      api_key: Optional[str] = None,
                      api_base: Optional[str] = None) -> AIReportEnhancer:
    """
    创建AI报告增强器的便捷函数
    
    Args:
        provider: AI提供商 ('openai', 'qwen', 'chatglm', 'local')
        model_name: 模型名称
        api_key: API密钥
        api_base: API基础URL
        
    Returns:
        AIReportEnhancer实例
    """
    # 从环境变量获取API密钥（如果未提供）
    if not api_key:
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "qwen": "QWEN_API_KEY", 
            "chatglm": "CHATGLM_API_KEY"
        }
        api_key = os.getenv(env_key_map.get(provider, "AI_API_KEY"))
    
    config = AIModelConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        api_base=api_base
    )
    
    return AIReportEnhancer(config)

# 预定义配置
DEFAULT_CONFIGS = {
    "openai_gpt35": AIModelConfig(
        provider="openai",
        model_name="gpt-3.5-turbo",
        max_tokens=4000,
        temperature=0.7
    ),
    "openai_gpt4": AIModelConfig(
        provider="openai", 
        model_name="gpt-4",
        max_tokens=4000,
        temperature=0.7
    ),
    "qwen_turbo": AIModelConfig(
        provider="qwen",
        model_name="qwen-turbo",
        max_tokens=4000,
        temperature=0.7
    ),
    "chatglm3": AIModelConfig(
        provider="chatglm",
        model_name="chatglm3-6b",
        max_tokens=4000,
        temperature=0.7
    ),
    "local_llama": AIModelConfig(
        provider="local",
        model_name="llama2",
        api_base="http://localhost:11434/api/generate",
        max_tokens=4000,
        temperature=0.7
    )
}