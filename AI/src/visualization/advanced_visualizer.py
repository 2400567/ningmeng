"""
增强版可视化模块
支持更多专业图表类型和学术发表级别的图表定制
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class AdvancedVisualizer:
    """高级可视化工具"""
    
    def __init__(self, style='academic'):
        """
        初始化可视化工具
        
        Args:
            style: 图表风格 ('academic', 'business', 'modern')
        """
        self.style = style
        self.color_palettes = {
            'academic': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#593E45'],
            'business': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'modern': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        }
        self.setup_style()
    
    def setup_style(self):
        """设置图表样式"""
        if self.style == 'academic':
            sns.set_style("whitegrid")
            plt.rcParams.update({
                'figure.figsize': (10, 6),
                'font.size': 12,
                'axes.labelsize': 14,
                'axes.titlesize': 16,
                'xtick.labelsize': 12,
                'ytick.labelsize': 12,
                'legend.fontsize': 12
            })
        elif self.style == 'business':
            sns.set_style("white")
            plt.rcParams.update({
                'figure.figsize': (12, 8),
                'font.size': 11,
                'axes.labelsize': 13,
                'axes.titlesize': 15
            })
    
    def create_descriptive_plots(self, data, variables, plot_type='comprehensive'):
        """
        创建描述性统计图表
        
        Args:
            data: DataFrame
            variables: 变量列表
            plot_type: 图表类型 ('comprehensive', 'distribution', 'summary')
        """
        if plot_type == 'comprehensive':
            return self._create_comprehensive_descriptive(data, variables)
        elif plot_type == 'distribution':
            return self._create_distribution_plots(data, variables)
        elif plot_type == 'summary':
            return self._create_summary_statistics_plot(data, variables)
    
    def _create_comprehensive_descriptive(self, data, variables):
        """创建综合描述性统计图表"""
        numeric_vars = [var for var in variables if data[var].dtype in ['int64', 'float64']]
        
        if len(numeric_vars) < 2:
            return None
        
        # 创建子图
        n_vars = len(numeric_vars)
        n_cols = min(3, n_vars)
        n_rows = (n_vars - 1) // n_cols + 1
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        colors = self.color_palettes[self.style]
        
        for i, var in enumerate(numeric_vars):
            row = i // n_cols
            col = i % n_cols
            ax = axes[row, col]
            
            # 绘制直方图和密度曲线
            ax.hist(data[var].dropna(), bins=30, alpha=0.7, color=colors[i % len(colors)], 
                   density=True, label='数据分布')
            
            # 添加正态分布拟合曲线
            mu, sigma = stats.norm.fit(data[var].dropna())
            x = np.linspace(data[var].min(), data[var].max(), 100)
            y = stats.norm.pdf(x, mu, sigma)
            ax.plot(x, y, 'r-', linewidth=2, label=f'正态拟合 (μ={mu:.2f}, σ={sigma:.2f})')
            
            # 添加统计信息
            mean_val = data[var].mean()
            median_val = data[var].median()
            ax.axvline(mean_val, color='green', linestyle='--', alpha=0.8, label=f'均值: {mean_val:.2f}')
            ax.axvline(median_val, color='orange', linestyle='--', alpha=0.8, label=f'中位数: {median_val:.2f}')
            
            ax.set_title(f'{var} 分布分析', fontsize=14, fontweight='bold')
            ax.set_xlabel(var)
            ax.set_ylabel('密度')
            ax.legend()
        
        # 隐藏多余的子图
        for i in range(n_vars, n_rows * n_cols):
            row = i // n_cols
            col = i % n_cols
            axes[row, col].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def create_correlation_heatmap(self, data, variables, method='pearson', annotate=True):
        """
        创建相关性热力图
        
        Args:
            data: DataFrame
            variables: 变量列表
            method: 相关性方法 ('pearson', 'spearman', 'kendall')
            annotate: 是否显示数值标注
        """
        numeric_vars = [var for var in variables if data[var].dtype in ['int64', 'float64']]
        
        if len(numeric_vars) < 2:
            return None
        
        # 计算相关性矩阵
        corr_matrix = data[numeric_vars].corr(method=method)
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 自定义颜色映射
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        
        # 绘制热力图
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # 只显示下三角
        sns.heatmap(corr_matrix, mask=mask, annot=annotate, cmap=cmap, center=0,
                   square=True, fmt='.3f', cbar_kws={"shrink": .8}, ax=ax)
        
        ax.set_title(f'{method.title()} 相关性分析热力图', fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def create_regression_plot(self, data, x_var, y_var, include_stats=True):
        """
        创建回归分析图
        
        Args:
            data: DataFrame
            x_var: 自变量
            y_var: 因变量
            include_stats: 是否包含统计信息
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 去除缺失值的有效数据
        valid_data = data[[x_var, y_var]].dropna()
        
        if len(valid_data) < 3:
            # 数据点太少，无法进行回归分析
            ax.text(0.5, 0.5, '数据点不足，无法进行回归分析', 
                   transform=ax.transAxes, ha='center', va='center', 
                   fontsize=14, color='red')
            return fig
        
        # 绘制散点图
        ax.scatter(valid_data[x_var], valid_data[y_var], alpha=0.6, 
                           color=self.color_palettes[self.style][0], s=50)
        
        # 回归线
        z = np.polyfit(valid_data[x_var], valid_data[y_var], 1)
        p = np.poly1d(z)
        x_range = np.linspace(valid_data[x_var].min(), valid_data[x_var].max(), 100)
        ax.plot(x_range, p(x_range), "r--", alpha=0.8, linewidth=2)
        
        # 计算统计指标
        if include_stats:
            corr_coef, p_value = stats.pearsonr(valid_data[x_var], valid_data[y_var])
            r_squared = corr_coef ** 2
            
            # 添加统计信息文本框
            stats_text = f'相关系数 r = {corr_coef:.3f}\n'
            stats_text += f'决定系数 R² = {r_squared:.3f}\n'
            stats_text += f'p值 = {p_value:.3f}\n'
            stats_text += f'显著性: {"**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"}'
            
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=11,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                   verticalalignment='top')
        
        ax.set_xlabel(x_var, fontsize=14)
        ax.set_ylabel(y_var, fontsize=14)
        ax.set_title(f'{x_var} vs {y_var} 回归分析', fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_box_plot_comparison(self, data, continuous_var, categorical_var):
        """
        创建分组箱线图比较
        
        Args:
            data: DataFrame
            continuous_var: 连续变量
            categorical_var: 分类变量
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 箱线图
        sns.boxplot(data=data, x=categorical_var, y=continuous_var, 
                   palette=self.color_palettes[self.style], ax=ax1)
        ax1.set_title(f'{continuous_var} 按 {categorical_var} 分组的箱线图', fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        
        # 小提琴图
        sns.violinplot(data=data, x=categorical_var, y=continuous_var, 
                      palette=self.color_palettes[self.style], ax=ax2)
        ax2.set_title(f'{continuous_var} 按 {categorical_var} 分组的小提琴图', fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_time_series_plot(self, data, date_col, value_cols, trend_analysis=True):
        """
        创建时间序列图
        
        Args:
            data: DataFrame
            date_col: 日期列
            value_cols: 数值列列表
            trend_analysis: 是否进行趋势分析
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = self.color_palettes[self.style]
        
        for i, col in enumerate(value_cols):
            ax.plot(data[date_col], data[col], 
                   color=colors[i % len(colors)], linewidth=2, 
                   marker='o', markersize=4, label=col)
            
            if trend_analysis:
                # 添加趋势线
                x_numeric = np.arange(len(data))
                z = np.polyfit(x_numeric, data[col].dropna(), 1)
                p = np.poly1d(z)
                ax.plot(data[date_col], p(x_numeric), 
                       color=colors[i % len(colors)], linestyle='--', alpha=0.7)
        
        ax.set_xlabel('时间', fontsize=14)
        ax.set_ylabel('数值', fontsize=14)
        ax.set_title('时间序列分析', fontsize=16, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    
    def create_statistical_report_chart(self, analysis_results):
        """
        创建统计分析报告图表
        
        Args:
            analysis_results: 统计分析结果
        """
        fig = plt.figure(figsize=(16, 12))
        
        # 创建网格布局
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. 描述性统计汇总
        ax1 = fig.add_subplot(gs[0, :])
        if 'descriptive_stats' in analysis_results:
            stats_data = analysis_results['descriptive_stats']
            stats_df = pd.DataFrame(stats_data).T
            
            # 创建表格
            table_data = []
            for var, stats in stats_data.items():
                table_data.append([
                    var, 
                    f"{stats['均值']:.2f}",
                    f"{stats['标准差']:.2f}",
                    f"{stats['最小值']:.2f}",
                    f"{stats['最大值']:.2f}",
                    stats['正态性']
                ])
            
            table = ax1.table(cellText=table_data,
                            colLabels=['变量', '均值', '标准差', '最小值', '最大值', '正态性'],
                            cellLoc='center',
                            loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.5)
            ax1.axis('off')
            ax1.set_title('描述性统计汇总', fontsize=14, fontweight='bold')
        
        # 2. 相关性矩阵
        ax2 = fig.add_subplot(gs[1, 0])
        if 'correlation_analysis' in analysis_results:
            corr_data = analysis_results['correlation_analysis']['correlation_matrix']
            sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, 
                       square=True, fmt='.2f', ax=ax2, cbar_kws={"shrink": .8})
            ax2.set_title('相关性矩阵', fontweight='bold')
        
        # 3. T检验结果
        ax3 = fig.add_subplot(gs[1, 1])
        if 't_test' in analysis_results:
            t_test_data = analysis_results['t_test']
            groups = ['组1', '组2']
            means = [t_test_data['group1_mean'], t_test_data['group2_mean']]
            stds = [t_test_data['group1_std'], t_test_data['group2_std']]
            
            x_pos = np.arange(len(groups))
            bars = ax3.bar(x_pos, means, yerr=stds, capsize=5, 
                          color=self.color_palettes[self.style][:2], alpha=0.7)
            ax3.set_xlabel('组别')
            ax3.set_ylabel('均值')
            ax3.set_title(f'T检验结果 (p={t_test_data["p_value"]:.3f})', fontweight='bold')
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels(groups)
            
            # 添加显著性标记
            if t_test_data['p_value'] < 0.05:
                ax3.text(0.5, max(means) + max(stds) * 0.1, 
                        '***' if t_test_data['p_value'] < 0.001 else '**' if t_test_data['p_value'] < 0.01 else '*',
                        ha='center', fontsize=16)
        
        # 4. 方差分析结果
        ax4 = fig.add_subplot(gs[1, 2])
        if 'anova' in analysis_results:
            anova_data = analysis_results['anova']
            groups = list(anova_data['descriptives'].keys())
            means = [stats['均值'] for stats in anova_data['descriptives'].values()]
            stds = [stats['标准差'] for stats in anova_data['descriptives'].values()]
            
            x_pos = np.arange(len(groups))
            bars = ax4.bar(x_pos, means, yerr=stds, capsize=5, 
                          color=self.color_palettes[self.style], alpha=0.7)
            ax4.set_xlabel('组别')
            ax4.set_ylabel('均值')
            ax4.set_title(f'方差分析 (F={anova_data["f_statistic"]:.2f})', fontweight='bold')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels(groups, rotation=45)
        
        # 5. 回归分析结果
        ax5 = fig.add_subplot(gs[2, :])
        if 'regression' in analysis_results:
            reg_data = analysis_results['regression']
            coefficients = reg_data['coefficients']
            
            vars_names = list(coefficients.keys())
            coef_values = [coef['coefficient'] for coef in coefficients.values()]
            
            bars = ax5.barh(vars_names, coef_values, 
                           color=self.color_palettes[self.style][0], alpha=0.7)
            ax5.set_xlabel('回归系数')
            ax5.set_title(f'回归分析结果 (R²={reg_data["r_squared"]:.3f})', fontweight='bold')
            ax5.axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        return fig
    
    def create_interactive_dashboard(self, data, analysis_results):
        """
        创建交互式仪表板（使用Plotly）
        
        Args:
            data: DataFrame
            analysis_results: 分析结果
        """
        # 创建子图布局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('数据分布', '相关性分析', '趋势分析', '统计汇总'),
            specs=[[{"type": "histogram"}, {"type": "heatmap"}],
                   [{"type": "scatter"}, {"type": "table"}]]
        )
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # 1. 直方图
            fig.add_trace(
                go.Histogram(x=data[numeric_cols[0]], name=numeric_cols[0], 
                           marker_color=self.color_palettes[self.style][0]),
                row=1, col=1
            )
            
            # 2. 相关性热力图
            corr_matrix = data[numeric_cols].corr()
            fig.add_trace(
                go.Heatmap(z=corr_matrix.values, 
                          x=corr_matrix.columns, 
                          y=corr_matrix.columns,
                          colorscale='RdBu',
                          zmid=0),
                row=1, col=2
            )
            
            # 3. 散点图
            fig.add_trace(
                go.Scatter(x=data[numeric_cols[0]], y=data[numeric_cols[1]], 
                          mode='markers', name=f'{numeric_cols[0]} vs {numeric_cols[1]}',
                          marker=dict(color=self.color_palettes[self.style][1])),
                row=2, col=1
            )
            
            # 4. 统计汇总表
            if 'descriptive_stats' in analysis_results:
                stats_data = analysis_results['descriptive_stats']
                table_headers = ['变量', '均值', '标准差', '最小值', '最大值']
                table_values = []
                
                for var, stats in stats_data.items():
                    table_values.append([
                        var,
                        f"{stats['均值']:.2f}",
                        f"{stats['标准差']:.2f}",
                        f"{stats['最小值']:.2f}",
                        f"{stats['最大值']:.2f}"
                    ])
                
                fig.add_trace(
                    go.Table(
                        header=dict(values=table_headers,
                                  fill_color='lightblue',
                                  align='center'),
                        cells=dict(values=list(zip(*table_values)),
                                 fill_color='lavender',
                                 align='center')
                    ),
                    row=2, col=2
                )
        
        fig.update_layout(
            title_text="数据分析交互式仪表板",
            title_x=0.5,
            showlegend=False,
            height=800
        )
        
        return fig
    
    def create_publication_ready_plot(self, data, plot_type, **kwargs):
        """
        创建发表级别的图表
        
        Args:
            data: DataFrame
            plot_type: 图表类型
            **kwargs: 其他参数
        """
        # 设置发表级别的样式
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'figure.figsize': (8, 6),
            'font.size': 12,
            'axes.labelsize': 14,
            'axes.titlesize': 16,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 12,
            'lines.linewidth': 2,
            'lines.markersize': 6,
            'figure.dpi': 300
        })
        
        if plot_type == 'correlation_publication':
            return self._create_publication_correlation(data, **kwargs)
        elif plot_type == 'regression_publication':
            return self._create_publication_regression(data, **kwargs)
        elif plot_type == 'comparison_publication':
            return self._create_publication_comparison(data, **kwargs)
    
    def _create_publication_correlation(self, data, variables):
        """创建发表级别的相关性图"""
        corr_matrix = data[variables].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 创建掩码矩阵
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        # 绘制热力图
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                   square=True, fmt='.3f', cbar_kws={"shrink": .8}, ax=ax,
                   linewidths=0.5)
        
        ax.set_title('Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
        
        # 设置刻度标签
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        
        plt.tight_layout()
        return fig
    
    def save_high_quality_plot(self, fig, filename, format='png', dpi=300):
        """
        保存高质量图表
        
        Args:
            fig: 图表对象
            filename: 文件名
            format: 格式 ('png', 'pdf', 'svg', 'eps')
            dpi: 分辨率
        """
        save_path = f"temp/figures/{filename}.{format}"
        fig.savefig(save_path, format=format, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        return save_path

class ChartTemplateLibrary:
    """图表模板库"""
    
    def __init__(self):
        self.templates = {
            "academic_paper": self._academic_paper_charts(),
            "business_report": self._business_report_charts(),
            "presentation": self._presentation_charts()
        }
    
    def _academic_paper_charts(self):
        """学术论文图表模板"""
        return {
            "figure_settings": {
                "figsize": (8, 6),
                "dpi": 300,
                "style": "seaborn-whitegrid",
                "color_palette": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]
            },
            "chart_types": {
                "correlation_heatmap": {
                    "title_format": "Correlation Matrix of Variables",
                    "annotation": True,
                    "colormap": "RdBu_r",
                    "center": 0
                },
                "regression_plot": {
                    "title_format": "Relationship between {x} and {y}",
                    "show_equation": True,
                    "show_r_squared": True,
                    "confidence_interval": True
                },
                "distribution_plot": {
                    "title_format": "Distribution of {variable}",
                    "show_normal_curve": True,
                    "show_statistics": True,
                    "bins": 30
                }
            }
        }
    
    def _business_report_charts(self):
        """商业报告图表模板"""
        return {
            "figure_settings": {
                "figsize": (12, 8),
                "dpi": 150,
                "style": "whitegrid",
                "color_palette": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
            },
            "chart_types": {
                "trend_chart": {
                    "title_format": "{metric} Trend Analysis",
                    "show_markers": True,
                    "show_trend_line": True,
                    "grid": True
                },
                "comparison_bar": {
                    "title_format": "{metric} Comparison",
                    "show_values": True,
                    "horizontal": False,
                    "sort_values": True
                }
            }
        }
    
    def get_template(self, template_type):
        """获取图表模板"""
        return self.templates.get(template_type, self.templates["academic_paper"])