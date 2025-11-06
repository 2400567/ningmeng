"""
SPSS风格数据分析模块
参考SPSSAU标准，提供专业的统计分析功能
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import pearsonr, spearmanr, chi2_contingency, ttest_ind, ttest_rel, f_oneway
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, classification_report
import warnings
warnings.filterwarnings('ignore')

class SPSSAnalyzer:
    """SPSS风格的数据分析器"""
    
    def __init__(self, data):
        """
        初始化分析器
        
        Args:
            data: pandas DataFrame
        """
        self.data = data
        self.numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
    def descriptive_statistics(self):
        """描述性统计分析"""
        results = {}
        
        for col in self.numeric_cols:
            desc = self.data[col].describe()
            
            # 计算偏度和峰度
            skewness = stats.skew(self.data[col].dropna())
            kurtosis = stats.kurtosis(self.data[col].dropna())
            
            # 正态性检验
            statistic, p_value = stats.shapiro(self.data[col].dropna()[:5000])  # 限制样本数量
            
            results[col] = {
                '样本量': desc['count'],
                '均值': desc['mean'],
                '标准差': desc['std'],
                '最小值': desc['min'],
                '25%分位数': desc['25%'],
                '中位数': desc['50%'],
                '75%分位数': desc['75%'],
                '最大值': desc['max'],
                '偏度': skewness,
                '峰度': kurtosis,
                '正态性检验统计量': statistic,
                '正态性检验p值': p_value,
                '正态性': '是' if p_value > 0.05 else '否'
            }
            
        return results
    
    def frequency_analysis(self, column):
        """频数分析"""
        if column not in self.data.columns:
            return None
            
        freq_table = self.data[column].value_counts()
        percent = (freq_table / len(self.data) * 100).round(2)
        
        result = pd.DataFrame({
            '频数': freq_table,
            '百分比': percent,
            '累积百分比': percent.cumsum()
        })
        
        return result
    
    def correlation_analysis(self, method='pearson'):
        """相关性分析"""
        if len(self.numeric_cols) < 2:
            return None
            
        numeric_data = self.data[self.numeric_cols]
        
        if method == 'pearson':
            corr_matrix = numeric_data.corr(method='pearson')
        elif method == 'spearman':
            corr_matrix = numeric_data.corr(method='spearman')
        
        # 计算p值
        p_values = np.zeros((len(self.numeric_cols), len(self.numeric_cols)))
        
        for i, col1 in enumerate(self.numeric_cols):
            for j, col2 in enumerate(self.numeric_cols):
                if i != j:
                    # 获取两个变量的有效观测值（成对删除缺失值）
                    valid_data = numeric_data[[col1, col2]].dropna()
                    if len(valid_data) >= 3:  # 至少需要3个观测值
                        if method == 'pearson':
                            _, p_val = pearsonr(valid_data[col1], valid_data[col2])
                        else:
                            _, p_val = spearmanr(valid_data[col1], valid_data[col2])
                        p_values[i, j] = p_val
                    else:
                        p_values[i, j] = np.nan
                else:
                    p_values[i, j] = 0
        
        p_values_df = pd.DataFrame(p_values, index=self.numeric_cols, columns=self.numeric_cols)
        
        return {
            'correlation_matrix': corr_matrix,
            'p_values': p_values_df,
            'interpretation': self._interpret_correlation(corr_matrix)
        }
    
    def t_test_independent(self, dependent_var, grouping_var):
        """独立样本T检验"""
        if dependent_var not in self.numeric_cols or grouping_var not in self.categorical_cols:
            return None
            
        groups = self.data[grouping_var].unique()
        if len(groups) != 2:
            return None
            
        group1_data = self.data[self.data[grouping_var] == groups[0]][dependent_var].dropna()
        group2_data = self.data[self.data[grouping_var] == groups[1]][dependent_var].dropna()
        
        # 方差齐性检验
        levene_stat, levene_p = stats.levene(group1_data, group2_data)
        
        # 独立样本T检验
        t_stat, p_value = ttest_ind(group1_data, group2_data, equal_var=(levene_p > 0.05))
        
        # 效应量计算（Cohen's d）
        pooled_std = np.sqrt(((len(group1_data)-1)*group1_data.var() + (len(group2_data)-1)*group2_data.var()) / (len(group1_data)+len(group2_data)-2))
        cohens_d = (group1_data.mean() - group2_data.mean()) / pooled_std
        
        return {
            'group1_mean': group1_data.mean(),
            'group1_std': group1_data.std(),
            'group1_n': len(group1_data),
            'group2_mean': group2_data.mean(),
            'group2_std': group2_data.std(),
            'group2_n': len(group2_data),
            'levene_statistic': levene_stat,
            'levene_p_value': levene_p,
            'variance_equal': '是' if levene_p > 0.05 else '否',
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'effect_size': self._interpret_effect_size(abs(cohens_d)),
            'significant': '是' if p_value < 0.05 else '否'
        }
    
    def anova_oneway(self, dependent_var, grouping_var):
        """单因子方差分析"""
        if dependent_var not in self.numeric_cols or grouping_var not in self.categorical_cols:
            return None
            
        groups = []
        group_names = []
        
        for group in self.data[grouping_var].unique():
            group_data = self.data[self.data[grouping_var] == group][dependent_var].dropna()
            if len(group_data) > 0:
                groups.append(group_data)
                group_names.append(group)
        
        if len(groups) < 2:
            return None
            
        # 方差分析
        f_stat, p_value = f_oneway(*groups)
        
        # 描述性统计
        descriptives = {}
        for i, (group_name, group_data) in enumerate(zip(group_names, groups)):
            descriptives[group_name] = {
                '样本量': len(group_data),
                '均值': group_data.mean(),
                '标准差': group_data.std(),
                '标准误': group_data.std() / np.sqrt(len(group_data))
            }
        
        return {
            'descriptives': descriptives,
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': '是' if p_value < 0.05 else '否',
            'groups_count': len(groups)
        }
    
    def chi_square_test(self, var1, var2):
        """卡方检验"""
        if var1 not in self.categorical_cols or var2 not in self.categorical_cols:
            return None
            
        contingency_table = pd.crosstab(self.data[var1], self.data[var2])
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        
        # Cramer's V 效应量
        n = contingency_table.sum().sum()
        cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))
        
        return {
            'contingency_table': contingency_table,
            'chi2_statistic': chi2,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'cramers_v': cramers_v,
            'effect_size': self._interpret_cramers_v(cramers_v),
            'significant': '是' if p_value < 0.05 else '否'
        }
    
    def linear_regression(self, dependent_var, independent_vars):
        """线性回归分析"""
        if dependent_var not in self.numeric_cols:
            return None
            
        valid_independent_vars = [var for var in independent_vars if var in self.numeric_cols]
        if not valid_independent_vars:
            return None
            
        # 准备数据
        data_for_regression = self.data[valid_independent_vars + [dependent_var]].dropna()
        X = data_for_regression[valid_independent_vars]
        y = data_for_regression[dependent_var]
        
        # 回归分析
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        # 计算统计量
        r2 = r2_score(y, y_pred)
        adjusted_r2 = 1 - (1 - r2) * (len(y) - 1) / (len(y) - len(valid_independent_vars) - 1)
        
        # 回归系数
        coefficients = {}
        for i, var in enumerate(valid_independent_vars):
            coefficients[var] = {
                'coefficient': model.coef_[i],
                'standardized_coefficient': model.coef_[i] * (X[var].std() / y.std())
            }
        
        return {
            'r_squared': r2,
            'adjusted_r_squared': adjusted_r2,
            'intercept': model.intercept_,
            'coefficients': coefficients,
            'n_observations': len(y),
            'n_predictors': len(valid_independent_vars)
        }
    
    def principal_component_analysis(self, variables=None):
        """主成分分析"""
        if variables is None:
            variables = self.numeric_cols
        else:
            variables = [var for var in variables if var in self.numeric_cols]
            
        if len(variables) < 2:
            return None
            
        # 数据标准化
        data_for_pca = self.data[variables].dropna()
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_for_pca)
        
        # PCA
        pca = PCA()
        components = pca.fit_transform(data_scaled)
        
        # 方差解释
        explained_variance_ratio = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance_ratio)
        
        # 成分载荷
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=[f'PC{i+1}' for i in range(len(variables))],
            index=variables
        )
        
        return {
            'explained_variance_ratio': explained_variance_ratio,
            'cumulative_variance': cumulative_variance,
            'loadings': loadings,
            'eigenvalues': pca.explained_variance_,
            'n_components': len(variables)
        }
    
    def cluster_analysis(self, variables=None, n_clusters=3):
        """聚类分析"""
        if variables is None:
            variables = self.numeric_cols
        else:
            variables = [var for var in variables if var in self.numeric_cols]
            
        if len(variables) < 2:
            return None
            
        # 数据标准化
        data_for_cluster = self.data[variables].dropna()
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_for_cluster)
        
        # K-means聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(data_scaled)
        
        # 聚类中心
        cluster_centers = pd.DataFrame(
            scaler.inverse_transform(kmeans.cluster_centers_),
            columns=variables,
            index=[f'Cluster {i+1}' for i in range(n_clusters)]
        )
        
        # 每个聚类的描述统计
        data_with_clusters = data_for_cluster.copy()
        data_with_clusters['Cluster'] = cluster_labels
        
        cluster_descriptions = {}
        for i in range(n_clusters):
            cluster_data = data_with_clusters[data_with_clusters['Cluster'] == i][variables]
            cluster_descriptions[f'Cluster {i+1}'] = {
                'size': len(cluster_data),
                'means': cluster_data.mean().to_dict()
            }
        
        return {
            'cluster_centers': cluster_centers,
            'cluster_descriptions': cluster_descriptions,
            'n_clusters': n_clusters,
            'inertia': kmeans.inertia_
        }
    
    def _interpret_correlation(self, corr_matrix):
        """解释相关系数"""
        interpretations = {}
        for col1 in corr_matrix.columns:
            for col2 in corr_matrix.columns:
                if col1 != col2:
                    corr_val = abs(corr_matrix.loc[col1, col2])
                    if corr_val >= 0.7:
                        strength = "强相关"
                    elif corr_val >= 0.3:
                        strength = "中等相关"
                    elif corr_val >= 0.1:
                        strength = "弱相关"
                    else:
                        strength = "极弱相关"
                    
                    interpretations[f"{col1} vs {col2}"] = strength
        
        return interpretations
    
    def _interpret_effect_size(self, cohens_d):
        """解释效应量"""
        if cohens_d < 0.2:
            return "小效应"
        elif cohens_d < 0.5:
            return "中等效应"
        elif cohens_d < 0.8:
            return "大效应"
        else:
            return "很大效应"
    
    def _interpret_cramers_v(self, cramers_v):
        """解释Cramer's V"""
        if cramers_v < 0.1:
            return "极弱关联"
        elif cramers_v < 0.3:
            return "弱关联"
        elif cramers_v < 0.5:
            return "中等关联"
        else:
            return "强关联"

class AdvancedAnalysis:
    """高级分析功能"""
    
    @staticmethod
    def reliability_analysis(data, items):
        """信度分析（Cronbach's Alpha）"""
        if len(items) < 2:
            return None
            
        item_data = data[items].dropna()
        
        # 计算Cronbach's Alpha
        item_variances = item_data.var()
        total_variance = item_data.sum(axis=1).var()
        k = len(items)
        
        alpha = (k / (k - 1)) * (1 - item_variances.sum() / total_variance)
        
        # 删除后的Alpha值
        alpha_if_deleted = {}
        for item in items:
            remaining_items = [i for i in items if i != item]
            remaining_data = item_data[remaining_items]
            remaining_variances = remaining_data.var()
            remaining_total_variance = remaining_data.sum(axis=1).var()
            k_remaining = len(remaining_items)
            
            alpha_remaining = (k_remaining / (k_remaining - 1)) * (1 - remaining_variances.sum() / remaining_total_variance)
            alpha_if_deleted[item] = alpha_remaining
        
        return {
            'cronbach_alpha': alpha,
            'alpha_if_item_deleted': alpha_if_deleted,
            'n_items': k,
            'n_cases': len(item_data)
        }
    
    @staticmethod
    def factor_analysis(data, variables):
        """因子分析"""
        # 这里可以使用factor_analyzer库，但为了简化，我们使用PCA作为替代
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        
        if len(variables) < 3:
            return None
            
        data_for_fa = data[variables].dropna()
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_for_fa)
        
        # 确定因子数量（Kaiser准则：特征值>1）
        pca_full = PCA()
        pca_full.fit(data_scaled)
        eigenvalues = pca_full.explained_variance_
        n_factors = sum(eigenvalues > 1)
        
        # 提取因子
        pca = PCA(n_components=n_factors)
        factor_scores = pca.fit_transform(data_scaled)
        
        # 因子载荷
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=[f'Factor{i+1}' for i in range(n_factors)],
            index=variables
        )
        
        return {
            'factor_loadings': loadings,
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'eigenvalues': eigenvalues[:n_factors],
            'n_factors': n_factors,
            'factor_scores': factor_scores
        }