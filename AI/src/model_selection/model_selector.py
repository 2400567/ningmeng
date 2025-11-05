"""
智能模型选择系统

根据数据特征自动推荐合适的分析模型，支持：
1. 回归分析
2. 分类分析
3. 聚类分析
4. 时间序列分析
5. 异常检测
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelRecommendation:
    """模型推荐结果数据类"""
    model_type: str
    model_name: str
    description: str
    suitability_score: float  # 0-100的匹配度分数
    reason: str
    required_params: Dict[str, Any] = None


def create_model_selector():
    """
    创建模型选择器实例的工厂函数
    
    Returns:
        ModelSelector: 模型选择器实例
    """
    return ModelSelector()

class ModelSelector:
    """智能模型选择器类"""
    
    def __init__(self):
        """初始化模型选择器"""
        self.logger = logging.getLogger(__name__)
        self.available_models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[str, Dict[str, Any]]:
        """初始化可用的分析模型库"""
        return {
            'regression': {
                'linear_regression': {
                    'description': '线性回归模型，适用于预测连续值',
                    'min_features': 1,
                    'min_samples': 20,
                    'supports_categorical': True,
                    'require_target': True,
                },
                'random_forest_regressor': {
                    'description': '随机森林回归，适用于复杂非线性关系预测',
                    'min_features': 1,
                    'min_samples': 50,
                    'supports_categorical': False,
                    'require_target': True,
                },
                'xgboost_regressor': {
                    'description': 'XGBoost回归，适用于高精度预测任务',
                    'min_features': 1,
                    'min_samples': 30,
                    'supports_categorical': False,
                    'require_target': True,
                }
            },
            'classification': {
                'logistic_regression': {
                    'description': '逻辑回归模型，适用于二分类问题',
                    'min_features': 1,
                    'min_samples': 30,
                    'max_classes': 2,
                    'supports_categorical': True,
                    'require_target': True,
                },
                'random_forest_classifier': {
                    'description': '随机森林分类器，适用于多分类问题',
                    'min_features': 1,
                    'min_samples': 50,
                    'supports_categorical': False,
                    'require_target': True,
                },
                'xgboost_classifier': {
                    'description': 'XGBoost分类器，适用于高精度分类任务',
                    'min_features': 1,
                    'min_samples': 30,
                    'supports_categorical': False,
                    'require_target': True,
                }
            },
            'clustering': {
                'kmeans': {
                    'description': 'K-means聚类算法，适用于数据分组',
                    'min_features': 2,
                    'min_samples': 50,
                    'supports_categorical': False,
                    'require_target': False,
                },
                'dbscan': {
                    'description': 'DBSCAN聚类算法，适用于发现任意形状的聚类',
                    'min_features': 2,
                    'min_samples': 30,
                    'supports_categorical': False,
                    'require_target': False,
                }
            },
            'time_series': {
                'arima': {
                    'description': 'ARIMA模型，适用于时间序列预测',
                    'min_features': 1,
                    'min_samples': 100,
                    'supports_categorical': False,
                    'require_target': True,
                    'requires_time_index': True,
                },
                'prophet': {
                    'description': 'Prophet模型，适用于具有季节性和趋势的时间序列预测',
                    'min_features': 1,
                    'min_samples': 50,
                    'supports_categorical': True,
                    'require_target': True,
                    'requires_time_index': True,
                }
            },
            'anomaly_detection': {
                'isolation_forest': {
                    'description': '隔离森林算法，适用于异常点检测',
                    'min_features': 2,
                    'min_samples': 100,
                    'supports_categorical': False,
                    'require_target': False,
                },
                'one_class_svm': {
                    'description': '单类SVM，适用于异常检测',
                    'min_features': 2,
                    'min_samples': 50,
                    'supports_categorical': False,
                    'require_target': False,
                }
            },
            'descriptive': {
                'descriptive_stats': {
                    'description': '描述性统计分析，提供数据概览',
                    'min_features': 1,
                    'min_samples': 1,
                    'supports_categorical': True,
                    'require_target': False,
                },
                'correlation_analysis': {
                    'description': '相关性分析，探索变量间关系',
                    'min_features': 2,
                    'min_samples': 10,
                    'supports_categorical': False,
                    'require_target': False,
                }
            }
        }
    
    def analyze_data_features(self, df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
        """
        分析数据特征
        
        Args:
            df: 数据框
            target_column: 目标列名（可选）
            
        Returns:
            Dict: 数据特征字典
        """
        features = {
            'n_rows': len(df),
            'n_columns': len(df.columns),
            'n_numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'n_categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
            'has_missing_values': df.isnull().sum().sum() > 0,
            'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns),
            'has_target': target_column is not None and target_column in df.columns,
        }
        
        # 检查是否可能是时间序列数据
        features['has_date_column'] = False
        date_columns = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]) or 'date' in col.lower() or 'time' in col.lower():
                date_columns.append(col)
                features['has_date_column'] = True
        features['date_columns'] = date_columns
        
        # 如果有目标列，分析目标列特征
        if features['has_target']:
            target_series = df[target_column]
            features['target_is_numeric'] = pd.api.types.is_numeric_dtype(target_series)
            
            if features['target_is_numeric']:
                features['target_type'] = 'regression'
                features['target_unique_values'] = target_series.nunique()
            else:
                features['target_type'] = 'classification'
                features['target_unique_values'] = target_series.nunique()
                features['target_classes'] = target_series.unique().tolist()
        
        self.logger.info(f"数据特征分析完成: {features}")
        return features
    
    def recommend_models(self, df: pd.DataFrame, target_column: str = None, 
                        user_preference: str = None, n_recommendations: int = 3) -> List[ModelRecommendation]:
        """
        根据数据特征推荐合适的模型
        
        Args:
            df: 数据框
            target_column: 目标列名（可选）
            user_preference: 用户偏好的模型类型（可选）
            n_recommendations: 推荐的模型数量
            
        Returns:
            List[ModelRecommendation]: 模型推荐列表
        """
        # 分析数据特征
        data_features = self.analyze_data_features(df, target_column)
        
        recommendations = []
        
        # 遍历所有可用模型
        for model_type, models in self.available_models.items():
            # 如果用户有偏好且当前模型类型不是用户偏好的，跳过
            if user_preference and model_type != user_preference:
                continue
                
            for model_name, model_info in models.items():
                # 计算匹配分数
                score, reason = self._calculate_model_score(model_type, model_name, model_info, data_features)
                
                if score > 0:  # 只有分数大于0的模型才被推荐
                    recommendation = ModelRecommendation(
                        model_type=model_type,
                        model_name=model_name,
                        description=model_info['description'],
                        suitability_score=score,
                        reason=reason
                    )
                    recommendations.append(recommendation)
        
        # 根据匹配分数排序
        recommendations.sort(key=lambda x: x.suitability_score, reverse=True)
        
        # 取前n个推荐
        top_recommendations = recommendations[:n_recommendations]
        
        self.logger.info(f"模型推荐完成，共推荐 {len(top_recommendations)} 个模型")
        return top_recommendations
    
    def _calculate_model_score(self, model_type: str, model_name: str, 
                              model_info: Dict[str, Any], data_features: Dict[str, Any]) -> Tuple[float, str]:
        """
        计算模型与数据的匹配分数
        
        Args:
            model_type: 模型类型
            model_name: 模型名称
            model_info: 模型信息
            data_features: 数据特征
            
        Returns:
            Tuple[float, str]: (匹配分数, 推荐理由)
        """
        score = 100  # 初始分数
        reasons = []
        
        # 检查是否需要目标列
        if model_info.get('require_target', False):
            if not data_features['has_target']:
                return 0, "需要指定目标列"
        
        # 检查最小特征数
        min_features = model_info.get('min_features', 1)
        if data_features['n_numeric_columns'] < min_features:
            missing = min_features - data_features['n_numeric_columns']
            score -= min(30, missing * 10)
            reasons.append(f"数值特征数量不足，建议至少有 {min_features} 个数值特征")
        
        # 检查最小样本数
        min_samples = model_info.get('min_samples', 1)
        if data_features['n_rows'] < min_samples:
            missing = min_samples - data_features['n_rows']
            score -= min(20, missing * 0.5)
            reasons.append(f"样本数量较少，建议至少有 {min_samples} 个样本")
        
        # 检查分类问题的类别数
        if model_type == 'classification' and data_features.get('target_is_numeric', False):
            # 如果目标列是数值型但实际上是分类问题，需要特殊处理
            if data_features.get('target_unique_values', 0) <= 20:
                reasons.append("注意：目标列是数值型但唯一值较少，可能是分类问题")
        
        # 检查时间序列模型
        if model_type == 'time_series' and 'requires_time_index' in model_info:
            if not data_features['has_date_column']:
                return 0, "时间序列模型需要日期或时间列"
        
        # 检查缺失值
        if data_features['missing_percentage'] > 50:
            score -= 15
            reasons.append("数据缺失率较高，可能影响模型效果")
        elif data_features['missing_percentage'] > 20:
            score -= 5
            reasons.append("数据有一定缺失，建议进行缺失值处理")
        
        # 根据模型类型调整分数
        if model_type == 'descriptive':
            # 描述性分析适用于几乎所有数据
            score = max(score, 80)
            if not reasons:
                reasons.append("适用于所有数据的基础分析")
        
        # 确保分数在0-100范围内
        score = max(0, min(100, score))
        
        # 生成推荐理由
        if not reasons:
            if model_type == 'regression':
                reasons.append("数据特征适合回归分析")
            elif model_type == 'classification':
                reasons.append("数据特征适合分类分析")
            elif model_type == 'clustering':
                reasons.append("数据特征适合聚类分析")
            elif model_type == 'time_series':
                reasons.append("数据特征适合时间序列分析")
            elif model_type == 'anomaly_detection':
                reasons.append("数据特征适合异常检测")
        
        return score, "；".join(reasons)
    
    def get_model_info(self, model_type: str, model_name: str) -> Dict[str, Any]:
        """
        获取指定模型的详细信息
        
        Args:
            model_type: 模型类型
            model_name: 模型名称
            
        Returns:
            Dict: 模型详细信息
        """
        if model_type in self.available_models:
            if model_name in self.available_models[model_type]:
                return self.available_models[model_type][model_name]
        raise ValueError(f"模型不存在: {model_type}.{model_name}")
    
    def get_supported_model_types(self) -> List[str]:
        """
        获取所有支持的模型类型
        
        Returns:
            List[str]: 模型类型列表
        """
        return list(self.available_models.keys())
    
    def get_models_by_type(self, model_type: str) -> List[str]:
        """
        获取指定类型的所有模型
        
        Args:
            model_type: 模型类型
            
        Returns:
            List[str]: 模型名称列表
        """
        if model_type in self.available_models:
            return list(self.available_models[model_type].keys())
        return []