"""
数据处理模块 - 提供数据清洗、特征提取和统计分析功能

主要功能：
1. 数据清洗 - 处理缺失值、异常值、重复值
2. 特征工程 - 特征提取、转换、选择
3. 统计分析 - 描述性统计、相关性分析
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectKBest, f_regression, f_classif, mutual_info_classif
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.logger = logging.getLogger(__name__)
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'mean', 
                            columns: List[str] = None, fill_value: Any = None) -> pd.DataFrame:
        """
        处理缺失值
        
        Args:
            df: 输入数据框
            strategy: 处理策略 - 'mean', 'median', 'mode', 'drop', 'fill', 'knn'
            columns: 要处理的列列表，None表示处理所有列
            fill_value: 当strategy为'fill'时使用的填充值
            
        Returns:
            pd.DataFrame: 处理后的数据框
        """
        df_copy = df.copy()
        
        # 确定要处理的列
        if columns is None:
            # 只处理数值型列
            columns = df_copy.select_dtypes(include=['number']).columns.tolist()
        else:
            # 确保所有指定的列都存在
            columns = [col for col in columns if col in df_copy.columns]
        
        self.logger.info(f"处理缺失值，策略: {strategy}，列数: {len(columns)}")
        
        try:
            if strategy == 'drop':
                # 删除包含缺失值的行
                df_copy = df_copy.dropna(subset=columns)
                self.logger.info(f"删除了 {len(df) - len(df_copy)} 行包含缺失值的数据")
            
            elif strategy == 'fill' and fill_value is not None:
                # 用指定值填充
                df_copy[columns] = df_copy[columns].fillna(fill_value)
                self.logger.info(f"用值 {fill_value} 填充缺失值")
            
            elif strategy == 'mean':
                # 用均值填充
                for col in columns:
                    if col in df_copy.select_dtypes(include=['number']).columns:
                        df_copy[col] = df_copy[col].fillna(df_copy[col].mean())
                self.logger.info(f"用均值填充缺失值")
            
            elif strategy == 'median':
                # 用中位数填充
                for col in columns:
                    if col in df_copy.select_dtypes(include=['number']).columns:
                        df_copy[col] = df_copy[col].fillna(df_copy[col].median())
                self.logger.info(f"用中位数填充缺失值")
            
            elif strategy == 'mode':
                # 用众数填充
                for col in columns:
                    mode_val = df_copy[col].mode()
                    if len(mode_val) > 0:
                        df_copy[col] = df_copy[col].fillna(mode_val[0])
                self.logger.info(f"用众数填充缺失值")
            
            elif strategy == 'knn':
                # 使用KNN填充
                imputer = KNNImputer(n_neighbors=5)
                numeric_cols = df_copy.select_dtypes(include=['number']).columns
                common_cols = [col for col in columns if col in numeric_cols]
                
                if common_cols:
                    df_copy[common_cols] = imputer.fit_transform(df_copy[common_cols])
                    self.logger.info(f"用KNN方法填充缺失值")
            
            else:
                raise ValueError(f"不支持的缺失值处理策略: {strategy}")
            
            return df_copy
            
        except Exception as e:
            self.logger.error(f"处理缺失值时出错: {str(e)}", exc_info=True)
            raise
    
    def handle_outliers(self, df: pd.DataFrame, columns: List[str] = None, 
                       method: str = 'zscore', threshold: float = 3.0) -> pd.DataFrame:
        """
        处理异常值
        
        Args:
            df: 输入数据框
            columns: 要处理的列列表，None表示处理所有数值型列
            method: 检测方法 - 'zscore', 'iqr', 'percentile'
            threshold: 阈值参数
            
        Returns:
            pd.DataFrame: 处理后的数据框
        """
        df_copy = df.copy()
        
        # 确定要处理的列
        if columns is None:
            columns = df_copy.select_dtypes(include=['number']).columns.tolist()
        else:
            columns = [col for col in columns if col in df_copy.columns and 
                      pd.api.types.is_numeric_dtype(df_copy[col])]
        
        self.logger.info(f"处理异常值，方法: {method}，阈值: {threshold}，列数: {len(columns)}")
        
        try:
            for col in columns:
                if method == 'zscore':
                    # 使用Z-score方法
                    z_scores = np.abs(stats.zscore(df_copy[col].dropna()))
                    outliers = df_copy[col].dropna()[z_scores > threshold].index
                    
                elif method == 'iqr':
                    # 使用IQR方法
                    Q1 = df_copy[col].quantile(0.25)
                    Q3 = df_copy[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    outliers = df_copy[(df_copy[col] < lower_bound) | 
                                      (df_copy[col] > upper_bound)].index
                
                elif method == 'percentile':
                    # 使用百分位数方法
                    lower_bound = df_copy[col].quantile(threshold / 100)
                    upper_bound = df_copy[col].quantile(1 - threshold / 100)
                    outliers = df_copy[(df_copy[col] < lower_bound) | 
                                      (df_copy[col] > upper_bound)].index
                
                else:
                    raise ValueError(f"不支持的异常值检测方法: {method}")
                
                # 将异常值替换为NaN（后续可以再处理）
                if len(outliers) > 0:
                    df_copy.loc[outliers, col] = np.nan
                    self.logger.info(f"列 {col}: 检测到 {len(outliers)} 个异常值")
            
            return df_copy
            
        except Exception as e:
            self.logger.error(f"处理异常值时出错: {str(e)}", exc_info=True)
            raise
    
    def remove_duplicates(self, df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """
        移除重复行
        
        Args:
            df: 输入数据框
            subset: 用于判断重复的列列表，None表示所有列
            
        Returns:
            pd.DataFrame: 去重后的数据框
        """
        initial_rows = len(df)
        df_copy = df.drop_duplicates(subset=subset)
        removed = initial_rows - len(df_copy)
        
        self.logger.info(f"移除了 {removed} 行重复数据")
        return df_copy
    
    def encode_categorical(self, df: pd.DataFrame, columns: List[str] = None, 
                          method: str = 'label') -> pd.DataFrame:
        """
        编码类别特征
        
        Args:
            df: 输入数据框
            columns: 要编码的列列表，None表示所有类别列
            method: 编码方法 - 'label', 'onehot'
            
        Returns:
            pd.DataFrame: 编码后的数据框
        """
        df_copy = df.copy()
        
        # 确定要编码的列
        if columns is None:
            columns = df_copy.select_dtypes(include=['object', 'category']).columns.tolist()
        else:
            columns = [col for col in columns if col in df_copy.columns and 
                      pd.api.types.is_object_dtype(df_copy[col]) or 
                      pd.api.types.is_categorical_dtype(df_copy[col])]
        
        self.logger.info(f"编码类别特征，方法: {method}，列数: {len(columns)}")
        
        try:
            if method == 'label':
                # 标签编码
                for col in columns:
                    le = LabelEncoder()
                    # 处理NaN值
                    df_copy[col] = df_copy[col].fillna('Missing')
                    df_copy[col] = le.fit_transform(df_copy[col])
            
            elif method == 'onehot':
                # 独热编码
                df_copy = pd.get_dummies(df_copy, columns=columns, drop_first=True)
            
            else:
                raise ValueError(f"不支持的编码方法: {method}")
            
            return df_copy
            
        except Exception as e:
            self.logger.error(f"编码类别特征时出错: {str(e)}", exc_info=True)
            raise
    
    def scale_features(self, df: pd.DataFrame, columns: List[str] = None, 
                      method: str = 'standard') -> pd.DataFrame:
        """
        缩放数值特征
        
        Args:
            df: 输入数据框
            columns: 要缩放的列列表，None表示所有数值型列
            method: 缩放方法 - 'standard', 'minmax'
            
        Returns:
            pd.DataFrame: 缩放后的数据框
        """
        df_copy = df.copy()
        
        # 确定要缩放的列
        if columns is None:
            columns = df_copy.select_dtypes(include=['number']).columns.tolist()
        else:
            columns = [col for col in columns if col in df_copy.columns and 
                      pd.api.types.is_numeric_dtype(df_copy[col])]
        
        self.logger.info(f"缩放数值特征，方法: {method}，列数: {len(columns)}")
        
        try:
            if method == 'standard':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()
            else:
                raise ValueError(f"不支持的缩放方法: {method}")
            
            # 应用缩放
            df_copy[columns] = scaler.fit_transform(df_copy[columns])
            return df_copy
            
        except Exception as e:
            self.logger.error(f"缩放特征时出错: {str(e)}", exc_info=True)
            raise
    
    def generate_descriptive_stats(self, df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """
        生成描述性统计
        
        Args:
            df: 输入数据框
            columns: 要分析的列列表，None表示所有列
            
        Returns:
            pd.DataFrame: 描述性统计结果
        """
        if columns is None:
            columns = df.columns.tolist()
        else:
            columns = [col for col in columns if col in df.columns]
        
        self.logger.info(f"生成描述性统计，列数: {len(columns)}")
        
        # 生成统计信息
        stats_df = df[columns].describe(include='all').T
        
        # 添加额外的统计信息
        if len(columns) > 0:
            stats_df['missing_count'] = df[columns].isnull().sum()
            stats_df['missing_percent'] = (stats_df['missing_count'] / len(df)) * 100
        
        return stats_df
    
    def calculate_correlation(self, df: pd.DataFrame, method: str = 'pearson', 
                             numeric_only: bool = True) -> pd.DataFrame:
        """
        计算相关性矩阵
        
        Args:
            df: 输入数据框
            method: 相关系数方法 - 'pearson', 'kendall', 'spearman'
            numeric_only: 是否只计算数值型列的相关性
            
        Returns:
            pd.DataFrame: 相关性矩阵
        """
        self.logger.info(f"计算相关性矩阵，方法: {method}")
        
        try:
            corr_matrix = df.corr(method=method, numeric_only=numeric_only)
            return corr_matrix
        except Exception as e:
            self.logger.error(f"计算相关性时出错: {str(e)}", exc_info=True)
            raise
    
    def select_features(self, X: pd.DataFrame, y: pd.Series, k: int = 10, 
                       task_type: str = 'regression') -> List[str]:
        """
        特征选择
        
        Args:
            X: 特征数据框
            y: 目标变量
            k: 要选择的特征数量
            task_type: 任务类型 - 'regression', 'classification'
            
        Returns:
            List[str]: 选择的特征列表
        """
        self.logger.info(f"进行特征选择，任务类型: {task_type}，选择特征数: {k}")
        
        try:
            # 选择合适的评分函数
            if task_type == 'regression':
                score_func = f_regression
            elif task_type == 'classification':
                # 检查目标变量是否是分类类型
                if y.nunique() > 10:  # 假设如果唯一值超过10个，可能是回归问题
                    raise ValueError("目标变量似乎是连续的，请使用回归任务类型")
                score_func = f_classif
            else:
                raise ValueError(f"不支持的任务类型: {task_type}")
            
            # 处理NaN值
            X_clean = X.fillna(X.mean())
            
            # 特征选择
            selector = SelectKBest(score_func=score_func, k=min(k, X.shape[1]))
            selector.fit(X_clean, y)
            
            # 获取选择的特征
            selected_indices = selector.get_support(indices=True)
            selected_features = X.columns[selected_indices].tolist()
            
            # 获取特征得分
            scores = selector.scores_
            feature_scores = pd.DataFrame({
                'feature': X.columns,
                'score': scores
            }).sort_values('score', ascending=False)
            
            self.logger.info(f"选择了 {len(selected_features)} 个特征")
            self.logger.info(f"前5个重要特征: {feature_scores.head().to_dict('records')}")
            
            return selected_features
            
        except Exception as e:
            self.logger.error(f"特征选择时出错: {str(e)}", exc_info=True)
            raise
    
    def detect_skewness(self, df: pd.DataFrame, columns: List[str] = None, 
                       threshold: float = 0.5) -> Dict[str, float]:
        """
        检测数据偏度
        
        Args:
            df: 输入数据框
            columns: 要分析的列列表，None表示所有数值型列
            threshold: 偏度阈值，超过此值认为存在显著偏度
            
        Returns:
            Dict[str, float]: 各列的偏度值
        """
        if columns is None:
            columns = df.select_dtypes(include=['number']).columns.tolist()
        else:
            columns = [col for col in columns if col in df.columns and 
                      pd.api.types.is_numeric_dtype(df[col])]
        
        skewness = {}
        for col in columns:
            skew_val = df[col].skew()
            skewness[col] = skew_val
            
            if abs(skew_val) > threshold:
                direction = '右偏' if skew_val > 0 else '左偏'
                self.logger.info(f"列 {col} 存在显著偏度 ({direction}，值: {skew_val:.3f})")
        
        return skewness
    
    def create_interaction_features(self, df: pd.DataFrame, 
                                  feature_pairs: List[Tuple[str, str]]) -> pd.DataFrame:
        """
        创建交互特征
        
        Args:
            df: 输入数据框
            feature_pairs: 要创建交互的特征对列表
            
        Returns:
            pd.DataFrame: 添加了交互特征的数据框
        """
        df_copy = df.copy()
        
        for col1, col2 in feature_pairs:
            if col1 in df_copy.columns and col2 in df_copy.columns:
                # 检查是否都是数值型
                if pd.api.types.is_numeric_dtype(df_copy[col1]) and \
                   pd.api.types.is_numeric_dtype(df_copy[col2]):
                    # 创建相乘的交互特征
                    new_col_name = f"{col1}_x_{col2}"
                    df_copy[new_col_name] = df_copy[col1] * df_copy[col2]
                    self.logger.info(f"创建交互特征: {new_col_name}")
        
        return df_copy
    
    def contrast_analysis(self, df: pd.DataFrame, group_column: str, 
                          value_columns: List[str] = None, 
                          method: str = 'mean') -> Dict[str, pd.DataFrame]:
        """
        反差分析 - 比较不同组或不同条件下的数据差异
        
        Args:
            df: 输入数据框
            group_column: 分组列名（用于区分不同的组）
            value_columns: 要分析的值列列表，None表示所有数值型列
            method: 聚合方法 - 'mean', 'median', 'sum', 'std'
            
        Returns:
            Dict[str, pd.DataFrame]: 分析结果字典，包含各组统计和差异分析
        """
        self.logger.info(f"进行反差分析，分组列: {group_column}，方法: {method}")
        
        # 验证分组列是否存在
        if group_column not in df.columns:
            raise ValueError(f"分组列 {group_column} 不存在于数据中")
        
        # 确定要分析的值列
        if value_columns is None:
            value_columns = df.select_dtypes(include=['number']).columns.tolist()
            # 排除分组列
            value_columns = [col for col in value_columns if col != group_column]
        else:
            value_columns = [col for col in value_columns if col in df.columns and 
                           pd.api.types.is_numeric_dtype(df[col])]
        
        if not value_columns:
            raise ValueError("没有有效的数值列用于分析")
        
        try:
            # 计算各组统计量
            group_stats = df.groupby(group_column)[value_columns].agg(method).round(4)
            
            # 计算组间差异
            groups = group_stats.index.tolist()
            contrasts = pd.DataFrame()
            
            if len(groups) > 1:
                # 对于每个数值列，计算各组间的差异
                for col in value_columns:
                    for i, group1 in enumerate(groups):
                        for j, group2 in enumerate(groups):
                            if i < j:  # 避免重复计算
                                diff_col = f"{group1}_vs_{group2}_{col}"
                                contrasts.loc[0, diff_col] = group_stats.loc[group1, col] - group_stats.loc[group2, col]
            
            # 计算总体统计量
            overall_stats = df[value_columns].agg(method).to_frame().T
            overall_stats.index = ['Overall']
            
            # 计算变异系数（用于衡量相对差异）
            cv_results = pd.DataFrame()
            for col in value_columns:
                col_mean = df[col].mean()
                col_std = df[col].std()
                cv_results.loc[0, f"{col}_CV"] = col_std / col_mean if col_mean != 0 else np.nan
            
            results = {
                'group_stats': group_stats,
                'contrasts': contrasts,
                'overall_stats': overall_stats,
                'cv_results': cv_results
            }
            
            self.logger.info(f"反差分析完成，分析了 {len(value_columns)} 个数值列")
            return results
            
        except Exception as e:
            self.logger.error(f"进行反差分析时出错: {str(e)}", exc_info=True)
            raise
    
    def cronbach_alpha(self, df: pd.DataFrame, scale_columns: List[str]) -> Dict:
        """
        计算克朗巴赫α系数，评估量表的内部一致性信度
        
        Args:
            df: 输入数据框
            scale_columns: 量表的项目列名列表
            
        Returns:
            Dict: 包含克朗巴赫α系数和相关统计信息的字典
        """
        self.logger.info(f"计算克朗巴赫α系数，量表项目数: {len(scale_columns)}")
        
        # 验证所有列是否存在且为数值型
        for col in scale_columns:
            if col not in df.columns:
                raise ValueError(f"列 {col} 不存在于数据中")
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"列 {col} 不是数值型数据")
        
        # 检查项目数
        if len(scale_columns) < 2:
            raise ValueError("至少需要2个项目来计算克朗巴赫α系数")
        
        try:
            # 选择量表项目列
            scale_df = df[scale_columns].copy()
            
            # 删除包含缺失值的行
            original_rows = len(scale_df)
            scale_df = scale_df.dropna()
            valid_rows = len(scale_df)
            
            if valid_rows == 0:
                raise ValueError("删除缺失值后没有有效数据")
            
            # 计算项目间相关系数矩阵
            correlation_matrix = scale_df.corr()
            
            # 计算项目数量
            k = len(scale_columns)
            
            # 计算项目方差
            item_variances = scale_df.var(axis=0)
            
            # 计算总分
            scale_df['total_score'] = scale_df.sum(axis=1)
            
            # 计算总分方差
            total_variance = scale_df['total_score'].var()
            
            # 计算克朗巴赫α系数
            # α = (k / (k - 1)) * (1 - (sum(item_variances) / total_variance))
            sum_item_variances = item_variances.sum()
            cronbach_alpha_value = (k / (k - 1)) * (1 - (sum_item_variances / total_variance)) if total_variance != 0 else 0
            
            # 计算平均项目间相关系数
            np.fill_diagonal(correlation_matrix.values, np.nan)
            mean_interitem_correlation = correlation_matrix.mean().mean()
            
            # 计算标准化后的α系数（基于相关系数矩阵）
            if mean_interitem_correlation == 1:
                standardized_alpha = 1.0
            else:
                standardized_alpha = (k * mean_interitem_correlation) / (1 + (k - 1) * mean_interitem_correlation) if k > 1 else 0
            
            # 计算每个项目删除后的α系数
            alpha_if_deleted = {}
            for col in scale_columns:
                remaining_cols = [c for c in scale_columns if c != col]
                remaining_df = df[remaining_cols].dropna()
                
                if len(remaining_df) > 0:
                    k_remaining = len(remaining_cols)
                    remaining_variances = remaining_df.var(axis=0)
                    remaining_df['total_score'] = remaining_df.sum(axis=1)
                    remaining_total_variance = remaining_df['total_score'].var()
                    
                    if remaining_total_variance != 0:
                        alpha_remaining = (k_remaining / (k_remaining - 1)) * (
                            1 - (remaining_variances.sum() / remaining_total_variance)
                        )
                        alpha_if_deleted[col] = alpha_remaining
                    else:
                        alpha_if_deleted[col] = 0
                else:
                    alpha_if_deleted[col] = 0
            
            # 信度解释
            if cronbach_alpha_value >= 0.9:
                reliability_interpretation = "优秀的内部一致性"
            elif cronbach_alpha_value >= 0.8:
                reliability_interpretation = "良好的内部一致性"
            elif cronbach_alpha_value >= 0.7:
                reliability_interpretation = "可接受的内部一致性"
            elif cronbach_alpha_value >= 0.6:
                reliability_interpretation = "一般的内部一致性"
            else:
                reliability_interpretation = "低内部一致性，建议修改量表"
            
            results = {
                'cronbach_alpha': round(cronbach_alpha_value, 4),
                'standardized_alpha': round(standardized_alpha, 4),
                'mean_interitem_correlation': round(mean_interitem_correlation, 4),
                'number_of_items': k,
                'valid_responses': valid_rows,
                'missing_responses': original_rows - valid_rows,
                'reliability_interpretation': reliability_interpretation,
                'item_statistics': {
                    'variances': item_variances.to_dict(),
                    'alpha_if_deleted': alpha_if_deleted
                },
                'correlation_matrix': correlation_matrix.round(4).to_dict()
            }
            
            self.logger.info(f"克朗巴赫α系数计算完成: {cronbach_alpha_value:.4f}")
            return results
            
        except Exception as e:
            self.logger.error(f"计算克朗巴赫α系数时出错: {str(e)}", exc_info=True)
            raise
    
    def reliability_analysis(self, df: pd.DataFrame, scale_columns: List[str], 
                            methods: List[str] = None) -> Dict[str, Dict]:
        """
        综合信度分析，支持多种信度指标
        
        Args:
            df: 输入数据框
            scale_columns: 量表的项目列名列表
            methods: 要计算的信度方法列表，默认包含['cronbach_alpha']
            
        Returns:
            Dict[str, Dict]: 各种信度分析结果的字典
        """
        self.logger.info(f"执行综合信度分析，方法: {methods}")
        
        if methods is None:
            methods = ['cronbach_alpha']
        
        results = {}
        
        # 执行克朗巴赫α系数计算
        if 'cronbach_alpha' in methods:
            results['cronbach_alpha'] = self.cronbach_alpha(df, scale_columns)
        
        # 可以在这里添加其他信度分析方法，如分半信度、重测信度等
        
        return results
    
    def factor_analysis_pca(self, df: pd.DataFrame, factor_columns: List[str], 
                           n_components: int = None) -> Dict:
        """
        使用主成分分析(PCA)进行因子分析，评估结构效度
        
        Args:
            df: 输入数据框
            factor_columns: 要进行因子分析的列名列表
            n_components: 要提取的主成分数量，None表示使用所有成分
            
        Returns:
            Dict: 因子分析结果字典
        """
        self.logger.info(f"执行PCA因子分析，分析列数: {len(factor_columns)}")
        
        # 验证所有列是否存在且为数值型
        for col in factor_columns:
            if col not in df.columns:
                raise ValueError(f"列 {col} 不存在于数据中")
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"列 {col} 不是数值型数据")
        
        try:
            # 选择分析列并删除缺失值
            analysis_df = df[factor_columns].copy()
            original_rows = len(analysis_df)
            analysis_df = analysis_df.dropna()
            valid_rows = len(analysis_df)
            
            if valid_rows == 0:
                raise ValueError("删除缺失值后没有有效数据")
            
            # 标准化数据
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(analysis_df)
            
            # 执行PCA
            pca = PCA(n_components=n_components)
            principal_components = pca.fit_transform(scaled_data)
            
            # 计算解释方差比
            explained_variance_ratio = pca.explained_variance_ratio_
            cumulative_variance_ratio = np.cumsum(explained_variance_ratio)
            
            # 获取因子载荷矩阵
            loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
            loading_matrix = pd.DataFrame(
                loadings, 
                columns=[f'Factor_{i+1}' for i in range(len(explained_variance_ratio))],
                index=factor_columns
            )
            
            # 计算公因子方差（共同度）
            communalities = np.sum(loading_matrix ** 2, axis=1)
            
            # 计算特征值
            eigenvalues = pca.explained_variance_
            
            # 确定保留的因子数量（基于Kaiser准则，特征值>1）
            kaiser_factors = sum(eigenvalues > 1)
            
            # 创建因子得分数据框
            factor_scores = pd.DataFrame(
                principal_components, 
                columns=[f'Factor_{i+1}' for i in range(len(explained_variance_ratio))]
            )
            
            # 计算每个原始变量与因子得分的相关系数（结构矩阵）
            structure_matrix = pd.DataFrame(
                np.corrcoef(analysis_df.T, factor_scores.T)[:len(factor_columns), len(factor_columns):],
                index=factor_columns,
                columns=[f'Factor_{i+1}' for i in range(len(explained_variance_ratio))]
            )
            
            results = {
                'loadings': loading_matrix.round(4).to_dict(),
                'structure_matrix': structure_matrix.round(4).to_dict(),
                'explained_variance_ratio': explained_variance_ratio.round(4).tolist(),
                'cumulative_variance_ratio': cumulative_variance_ratio.round(4).tolist(),
                'eigenvalues': eigenvalues.round(4).tolist(),
                'communalities': communalities.round(4).to_dict(),
                'kaiser_factors': kaiser_factors,
                'valid_responses': valid_rows,
                'missing_responses': original_rows - valid_rows,
                'n_components': len(explained_variance_ratio)
            }
            
            self.logger.info(f"PCA因子分析完成，提取了 {len(explained_variance_ratio)} 个主成分")
            return results
            
        except Exception as e:
            self.logger.error(f"执行PCA因子分析时出错: {str(e)}", exc_info=True)
            raise
    
    def criterion_validity(self, df: pd.DataFrame, scale_columns: List[str], 
                          criterion_column: str) -> Dict:
        """
        计算效标效度，通过分析量表分数与效标变量之间的相关性
        
        Args:
            df: 输入数据框
            scale_columns: 量表的项目列名列表
            criterion_column: 效标变量列名
            
        Returns:
            Dict: 效标效度分析结果字典
        """
        self.logger.info(f"计算效标效度，量表项目数: {len(scale_columns)}")
        
        # 验证所有列是否存在且为数值型
        for col in scale_columns + [criterion_column]:
            if col not in df.columns:
                raise ValueError(f"列 {col} 不存在于数据中")
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"列 {col} 不是数值型数据")
        
        try:
            # 创建分析数据框
            analysis_df = df[scale_columns + [criterion_column]].copy()
            
            # 计算量表总分
            analysis_df['scale_total'] = analysis_df[scale_columns].sum(axis=1)
            
            # 删除缺失值
            original_rows = len(analysis_df)
            analysis_df = analysis_df.dropna()
            valid_rows = len(analysis_df)
            
            if valid_rows == 0:
                raise ValueError("删除缺失值后没有有效数据")
            
            # 计算总分与效标变量的相关系数
            total_correlation = stats.pearsonr(analysis_df['scale_total'], analysis_df[criterion_column])
            
            # 计算每个项目与效标变量的相关系数
            item_correlations = {}
            for col in scale_columns:
                corr = stats.pearsonr(analysis_df[col], analysis_df[criterion_column])
                item_correlations[col] = {
                    'correlation': round(corr[0], 4),
                    'p_value': round(corr[1], 6)
                }
            
            # 效标效度解释
            correlation_value = abs(total_correlation[0])
            if correlation_value >= 0.7:
                validity_interpretation = "高效标效度"
            elif correlation_value >= 0.5:
                validity_interpretation = "中等效标效度"
            elif correlation_value >= 0.3:
                validity_interpretation = "低效标效度"
            else:
                validity_interpretation = "极低效标效度"
            
            results = {
                'total_correlation': round(total_correlation[0], 4),
                'total_p_value': round(total_correlation[1], 6),
                'item_correlations': item_correlations,
                'validity_interpretation': validity_interpretation,
                'valid_responses': valid_rows,
                'missing_responses': original_rows - valid_rows
            }
            
            self.logger.info(f"效标效度计算完成，总分相关系数: {total_correlation[0]:.4f}")
            return results
            
        except Exception as e:
            self.logger.error(f"计算效标效度时出错: {str(e)}", exc_info=True)
            raise
    
    def validity_analysis(self, df: pd.DataFrame, scale_columns: List[str], 
                         methods: Dict = None) -> Dict[str, Dict]:
        """
        综合效度分析，支持多种效度评估方法
        
        Args:
            df: 输入数据框
            scale_columns: 量表的项目列名列表
            methods: 要使用的效度方法配置，格式为{'method_name': parameters}
                     默认包含结构效度分析
            
        Returns:
            Dict[str, Dict]: 各种效度分析结果的字典
        """
        self.logger.info(f"执行综合效度分析")
        
        if methods is None:
            methods = {'factor_analysis': {'n_components': None}}
        
        results = {}
        
        # 执行因子分析（结构效度）
        if 'factor_analysis' in methods:
            params = methods['factor_analysis']
            results['structure_validity'] = self.factor_analysis_pca(
                df, scale_columns, 
                n_components=params.get('n_components', None)
            )
        
        # 执行效标效度分析
        if 'criterion_validity' in methods:
            params = methods['criterion_validity']
            if 'criterion_column' in params:
                results['criterion_validity'] = self.criterion_validity(
                    df, scale_columns, 
                    criterion_column=params['criterion_column']
                )
        
        return results