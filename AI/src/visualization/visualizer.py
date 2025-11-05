import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import base64
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from matplotlib.figure import Figure
import plotly.express as px
import plotly.graph_objects as go

class DataVisualizer:
    """
    数据可视化工具类，提供多种图表生成功能
    """
    
    def __init__(self):
        # 设置中文字体支持：优先使用系统中可用的中文字体（Noto、WenQuanYi、SimHei 等），
        # 否则回退到 DejaVu Sans。这样可以避免大量中文缺字警告并提高渲染稳定性。
        try:
            from matplotlib import font_manager as fm
            from matplotlib.font_manager import FontProperties
            # 优先查找 Noto / WenQuanYi 字体文件并读取其内部 family name
            candidate_dirs = [
                '/usr/share/fonts/opentype/noto',
                '/usr/share/fonts/truetype/wqy',
                '/usr/share/fonts/truetype',
                '/usr/local/share/fonts',
                '/usr/share/fonts'
            ]
            chosen_name = None
            for d in candidate_dirs:
                try:
                    p = Path(d)
                    if not p.exists():
                        continue
                    for f in sorted(p.rglob('*')):
                        if f.suffix.lower() in ['.ttf', '.otf', '.ttc']:
                            # 只挑选可能包含 CJK 的字体文件名（加速匹配）
                            if 'Noto' in f.name or 'WenQuan' in f.name or 'WenQuanYi' in f.name or 'SimHei' in f.name or 'Microsoft' in f.name:
                                try:
                                    fp = FontProperties(fname=str(f))
                                    name = fp.get_name()
                                    if name:
                                        chosen_name = name
                                        break
                                except Exception:
                                    continue
                    if chosen_name:
                        break
                except Exception:
                    continue

            if chosen_name:
                plt.rcParams['font.sans-serif'] = [chosen_name, 'DejaVu Sans']
            else:
                # 回退：尝试从已注册字体中找包含 Noto 或 SimHei 的 family
                font_names = [f.name for f in fm.fontManager.ttflist]
                for sub in ['Noto', 'WenQuan', 'SimHei', 'Microsoft YaHei', 'AR PL']:
                    for name in font_names:
                        if sub in name:
                            chosen_name = name
                            break
                    if chosen_name:
                        break
                plt.rcParams['font.sans-serif'] = [chosen_name] if chosen_name else ['DejaVu Sans']
        except Exception:
            # 如果任何检测出错，保证至少有一个回退字体，避免抛出异常
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

        plt.rcParams['axes.unicode_minus'] = False
        sns.set_style("whitegrid")
        
    def create_bar_chart(self, data: pd.DataFrame, x_column: str, y_column: str, 
                        title: str = "柱状图", figsize: Tuple[int, int] = (10, 6),
                        color: str = "#1f77b4", horizontal: bool = False,
                        top_n: Optional[int] = None) -> Figure:
        """
        创建柱状图
        
        Args:
            data: 数据框
            x_column: X轴列名
            y_column: Y轴列名
            title: 图表标题
            figsize: 图表尺寸
            color: 柱子颜色
            horizontal: 是否水平显示
            top_n: 显示前N个值
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 如果只显示前N个值
        if top_n:
            data = data.nlargest(top_n, y_column)
        
        if horizontal:
            bars = ax.barh(data[x_column], data[y_column], color=color, alpha=0.8)
            ax.set_xlabel(y_column)
            ax.set_ylabel(x_column)
        else:
            bars = ax.bar(data[x_column], data[y_column], color=color, alpha=0.8)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
        
        ax.set_title(title)
        ax.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar in bars:
            if horizontal:
                width = bar.get_width()
                ax.text(width + max(data[y_column])*0.01, bar.get_y() + bar.get_height()/2,
                        f'{width:.2f}', ha='left', va='center')
            else:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height + max(data[y_column])*0.01,
                        f'{height:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def create_line_chart(self, data: pd.DataFrame, x_column: str, y_columns: Union[str, List[str]],
                         title: str = "折线图", figsize: Tuple[int, int] = (10, 6),
                         colors: Optional[List[str]] = None, markers: bool = True) -> Figure:
        """
        创建折线图
        
        Args:
            data: 数据框
            x_column: X轴列名
            y_columns: Y轴列名或列名列表
            title: 图表标题
            figsize: 图表尺寸
            colors: 线条颜色列表
            markers: 是否显示标记点
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)

        if isinstance(y_columns, str):
            y_columns = [y_columns]

        if colors is None:
            colors = plt.cm.tab10.colors[:len(y_columns)]

        for i, y_col in enumerate(y_columns):
            # Align x and y by dropping rows where either is NaN
            if x_column not in data.columns or y_col not in data.columns:
                print(f"跳过列: {x_column} 或 {y_col} 不在数据中")
                continue

            df_pair = data[[x_column, y_col]].dropna()
            if df_pair.empty:
                print(f"跳过列 {y_col}: 没有有效的数据点")
                continue

            marker = 'o' if markers else None
            ax.plot(df_pair[x_column], df_pair[y_col], label=y_col, color=colors[i % len(colors)], marker=marker, alpha=0.8)

        ax.set_xlabel(x_column)
        ax.set_ylabel("值")
        ax.set_title(title)
        ax.legend()
        plt.tight_layout()
        return fig
    
    def create_scatter_plot(self, data: pd.DataFrame, x_column: str, y_column: str,
                          title: str = "散点图", figsize: Tuple[int, int] = (10, 6),
                          color: str = "#1f77b4", size: Optional[str] = None,
                          trendline: bool = False, hue: Optional[str] = None) -> Figure:
        """
        创建散点图
        
        Args:
            data: 数据框
            x_column: X轴列名
            y_column: Y轴列名
            title: 图表标题
            figsize: 图表尺寸
            color: 点的颜色
            size: 点大小对应的列名
            trendline: 是否显示趋势线
            hue: 分组着色的列名
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Helper to safely get paired x/y (and optional size) arrays
        def _get_paired_df(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
            available = [c for c in cols if c in df.columns]
            if not available or len(available) < 2:
                return pd.DataFrame()
            return df[available].dropna()

        if hue and hue in data.columns:
            # 分组散点图
            groups = data.groupby(hue)
            colors = plt.cm.tab10.colors[:max(1, len(groups))]

            for i, (name, group) in enumerate(groups):
                cols = [x_column, y_column]
                if size:
                    cols.append(size)

                df_group = _get_paired_df(group, cols)
                if df_group.empty:
                    print(f"跳过分组 {name}: 没有足够的有效数据点")
                    continue

                scatter_kws = {}
                if size and size in df_group.columns:
                    scatter_kws['s'] = df_group[size]

                ax.scatter(df_group[x_column], df_group[y_column], label=name,
                           color=colors[i % len(colors)], alpha=0.7, **scatter_kws)

            ax.legend(title=hue)
        else:
            # 普通散点图 — 对 x/y 和 size 同步 dropna
            cols = [x_column, y_column]
            if size:
                cols.append(size)

            df_pair = _get_paired_df(data, cols)
            if df_pair.empty:
                print(f"没有足够的数据绘制散点图: 列 {cols} 缺失或均为 NaN")
            else:
                scatter_kws = {}
                if size and size in df_pair.columns:
                    scatter_kws['s'] = df_pair[size]

                ax.scatter(df_pair[x_column], df_pair[y_column], color=color, alpha=0.7, **scatter_kws)

        # 添加趋势线（基于已对齐的数据）
        if trendline:
            try:
                df_t = _get_paired_df(data, [x_column, y_column])
                if df_t.empty:
                    print("无法计算趋势线: 没有足够的有效配对数据点")
                else:
                    z = np.polyfit(df_t[x_column], df_t[y_column], 1)
                    p = np.poly1d(z)
                    ax.plot(df_t[x_column], p(df_t[x_column]), "r--", alpha=0.8)

                    # 添加相关系数
                    corr = df_t[[x_column, y_column]].corr().iloc[0, 1]
                    ax.annotate(f'相关系数: {corr:.3f}',
                               xy=(0.05, 0.95), xycoords='axes fraction',
                               fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7))
            except Exception as e:
                print(f"绘制趋势线时出错: {e}")

        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        ax.set_title(title)
        plt.tight_layout()
        return fig
    
    def create_heatmap(self, data: pd.DataFrame, title: str = "热力图",
                      figsize: Tuple[int, int] = (12, 10), cmap: str = "coolwarm",
                      annot: bool = True, vmin: Optional[float] = None,
                      vmax: Optional[float] = None) -> Figure:
        """
        创建热力图（适用于相关性矩阵）
        
        Args:
            data: 相关性矩阵或数据框
            title: 图表标题
            figsize: 图表尺寸
            cmap: 颜色映射
            annot: 是否显示数值
            vmin: 最小值
            vmax: 最大值
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 如果数据不是相关矩阵，自动计算相关性
        if not self._is_square_matrix(data):
            numeric_data = data.select_dtypes(include=[np.number])
            data = numeric_data.corr()
        
        # 创建掩码以只显示下三角矩阵
        mask = np.triu(np.ones_like(data, dtype=bool))
        
        sns.heatmap(data, annot=annot, cmap=cmap, mask=mask, vmin=vmin, vmax=vmax,
                   square=True, linewidths=.5, cbar_kws={"shrink": .8}, ax=ax)
        
        ax.set_title(title)
        plt.tight_layout()
        return fig
    
    def create_histogram(self, data: pd.DataFrame, column: str, bins: int = 30,
                        title: str = "直方图", figsize: Tuple[int, int] = (10, 6),
                        color: str = "#1f77b4", kde: bool = True) -> Figure:
        """
        创建直方图
        
        Args:
            data: 数据框
            column: 要分析的列名
            bins: 直方图的柱数
            title: 图表标题
            figsize: 图表尺寸
            color: 直方图颜色
            kde: 是否显示密度曲线
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.histplot(data=data, x=column, bins=bins, color=color, kde=kde, ax=ax)
        
        # 添加统计信息
        mean_val = data[column].mean()
        median_val = data[column].median()
        
        ax.axvline(mean_val, color='r', linestyle='--', label=f'均值: {mean_val:.2f}')
        ax.axvline(median_val, color='g', linestyle='--', label=f'中位数: {median_val:.2f}')
        
        ax.set_xlabel(column)
        ax.set_ylabel("频率")
        ax.set_title(title)
        ax.legend()
        plt.tight_layout()
        return fig
    
    def create_box_plot(self, data: pd.DataFrame, x_column: Optional[str] = None,
                       y_column: str = None, title: str = "箱线图",
                       figsize: Tuple[int, int] = (10, 6), color: str = "#1f77b4") -> Figure:
        """
        创建箱线图
        
        Args:
            data: 数据框
            x_column: X轴列名（分类变量）
            y_column: Y轴列名（数值变量）
            title: 图表标题
            figsize: 图表尺寸
            color: 箱线图颜色
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if x_column:
            sns.boxplot(x=x_column, y=y_column, data=data, ax=ax, color=color)
        else:
            sns.boxplot(data=data[y_column], ax=ax, color=color)
        
        # 添加异常值标记
        if x_column:
            for i, group in enumerate(data.groupby(x_column)[y_column]):
                values = group[1]
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                outliers = values[(values < Q1 - 1.5 * IQR) | (values > Q3 + 1.5 * IQR)]
                
                if not outliers.empty:
                    # 添加异常值数量标签
                    ax.annotate(f'异常值: {len(outliers)}',
                               xy=(i, values.max()), xytext=(i, values.max() * 1.05),
                               ha='center', color='red', fontsize=8)
        
        ax.set_title(title)
        plt.tight_layout()
        return fig
    
    def create_pie_chart(self, data: pd.DataFrame, value_column: str, 
                        label_column: str, title: str = "饼图",
                        figsize: Tuple[int, int] = (10, 8), autopct: str = "%1.1f%%",
                        top_n: Optional[int] = None) -> Figure:
        """
        创建饼图
        
        Args:
            data: 数据框
            value_column: 数值列名
            label_column: 标签列名
            title: 图表标题
            figsize: 图表尺寸
            autopct: 百分比格式
            top_n: 显示前N个类别，其余合并为"其他"
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 处理前N个类别
        if top_n and len(data) > top_n:
            top_data = data.nlargest(top_n, value_column).copy()
            others_sum = data[~data[label_column].isin(top_data[label_column])][value_column].sum()
            
            if others_sum > 0:
                others_row = pd.DataFrame([[others_sum, "其他"]], columns=[value_column, label_column])
                top_data = pd.concat([top_data, others_row], ignore_index=True)
            
            data = top_data
        
        # 创建饼图
        wedges, texts, autotexts = ax.pie(data[value_column], labels=data[label_column],
                                        autopct=autopct, startangle=90, shadow=False)
        
        # 设置文本样式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
        
        ax.axis('equal')  # 确保饼图是圆的
        ax.set_title(title)
        plt.tight_layout()
        return fig
    
    def create_radar_chart(self, data: pd.DataFrame, categories: List[str],
                          values: List[float], title: str = "雷达图",
                          figsize: Tuple[int, int] = (10, 8), color: str = "#1f77b4") -> Figure:
        """
        创建雷达图
        
        Args:
            data: 数据框（可选，用于多组数据）
            categories: 类别列表
            values: 值列表
            title: 图表标题
            figsize: 图表尺寸
            color: 线条颜色
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
        
        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合雷达图
        
        # 处理值
        values += values[:1]  # 闭合雷达图
        
        # 绘制雷达图
        ax.plot(angles, values, color=color, linewidth=2, marker='o')
        ax.fill(angles, values, color=color, alpha=0.25)
        
        # 设置标签
        ax.set_thetagrids(np.degrees(angles[:-1]), categories)
        ax.set_ylim(0, max(values) * 1.2)
        ax.set_title(title)
        ax.grid(True)
        
        plt.tight_layout()
        return fig
    
    def figure_to_base64(self, fig: Figure) -> str:
        """
        将matplotlib Figure转换为base64字符串
        
        Args:
            fig: matplotlib Figure对象
            
        Returns:
            base64编码的字符串
        """
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        plt.close(fig)
        return image_base64
    
    def create_interactive_scatter(self, data: pd.DataFrame, x_column: str, y_column: str,
                                 title: str = "交互式散点图", color: Optional[str] = None,
                                 size: Optional[str] = None, hover_data: Optional[List[str]] = None) -> go.Figure:
        """
        创建交互式散点图（Plotly）
        
        Args:
            data: 数据框
            x_column: X轴列名
            y_column: Y轴列名
            title: 图表标题
            color: 着色列名
            size: 点大小列名
            hover_data: 悬停时显示的数据列
            
        Returns:
            Plotly Figure对象
        """
        fig = px.scatter(
            data, x=x_column, y=y_column, color=color,
            size=size, hover_data=hover_data, title=title
        )
        
        fig.update_layout(
            font=dict(family="SimHei, sans-serif"),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        return fig
    
    def create_interactive_histogram(self, data: pd.DataFrame, x_column: str,
                                   title: str = "交互式直方图", color: Optional[str] = None,
                                   nbins: int = 30) -> go.Figure:
        """
        创建交互式直方图（Plotly）
        
        Args:
            data: 数据框
            x_column: 列名
            title: 图表标题
            color: 着色列名
            nbins: 柱数
            
        Returns:
            Plotly Figure对象
        """
        fig = px.histogram(
            data, x=x_column, color=color, nbins=nbins, title=title,
            marginal="box"  # 添加箱线图边际分布
        )
        
        fig.update_layout(
            font=dict(family="SimHei, sans-serif"),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        return fig
    
    def _is_square_matrix(self, data: pd.DataFrame) -> bool:
        """
        检查数据框是否为方阵
        
        Args:
            data: 数据框
            
        Returns:
            是否为方阵
        """
        return data.shape[0] == data.shape[1] and set(data.index) == set(data.columns)

# 创建可视化功能类
class VisualizationManager:
    """
    可视化管理器，协调各类图表的创建和管理
    """
    
    def __init__(self):
        self.visualizer = DataVisualizer()
        self.created_charts = {}
    
    def create_scatter_plot(self, data: pd.DataFrame, x_col: str, y_col: str,
                          title: str = "散点图", figsize: Tuple[int, int] = (10, 6),
                          color: str = "#1f77b4", size: Optional[str] = None,
                          trendline: bool = False, hue: Optional[str] = None) -> Figure:
        """
        创建散点图（包装DataVisualizer的方法）
        
        Args:
            data: 数据框
            x_col: X轴列名
            y_col: Y轴列名
            title: 图表标题
            figsize: 图表尺寸
            color: 点的颜色
            size: 点大小对应的列名
            trendline: 是否显示趋势线
            hue: 分组着色的列名
            
        Returns:
            matplotlib Figure对象
        """
        # 转换参数名以匹配DataVisualizer的方法
        return self.visualizer.create_scatter_plot(data, x_col, y_col, title, 
                                                 figsize, color, size, trendline, hue)
    
    def recommend_charts(self, data):
        """
        根据数据特征推荐合适的图表类型
        
        Args:
            data: pandas DataFrame，包含要分析的数据
            
        Returns:
            list: 推荐的图表类型列表，每个元素是字典，包含图表类型和推荐理由
        """
        recommendations = []
        
        # 分析数据特征
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
        
        # 检查是否有日期列
        for col in data.columns:
            if data[col].dtype == 'object':
                try:
                    pd.to_datetime(data[col])
                    date_cols.append(col)
                except:
                    pass
        
        # 根据不同数据特征推荐图表
        
        # 散点图：如果有至少两个数值列
        if len(numeric_cols) >= 2:
            recommendations.append({
                'chart_type': '散点图',
                'reason': f'数据包含{len(numeric_cols)}个数值列，适合使用散点图分析变量间关系'
            })
        
        # 柱状图：如果有类别列和数值列
        if categorical_cols and numeric_cols:
            recommendations.append({
                'chart_type': '柱状图',
                'reason': f'数据包含类别列和数值列，适合使用柱状图比较不同类别的数值'
            })
        
        # 直方图：如果有数值列
        if numeric_cols:
            recommendations.append({
                'chart_type': '直方图',
                'reason': f'数据包含数值列，适合使用直方图展示数据分布'
            })
        
        # 折线图：如果有日期列和数值列
        if date_cols and numeric_cols:
            recommendations.append({
                'chart_type': '折线图',
                'reason': f'数据包含日期列，适合使用折线图展示时间趋势'
            })
        
        # 热力图：如果有多个数值列
        if len(numeric_cols) >= 3:
            recommendations.append({
                'chart_type': '热力图',
                'reason': f'数据包含多个数值列，适合使用热力图展示相关性'
            })
        
        # 箱线图：如果有数值列
        if numeric_cols:
            recommendations.append({
                'chart_type': '箱线图',
                'reason': f'数据包含数值列，适合使用箱线图识别异常值和数据分布'
            })
        
        # 饼图：如果有类别列且样本量不太大
        if categorical_cols and len(data) <= 200:
            recommendations.append({
                'chart_type': '饼图',
                'reason': f'数据包含类别列，适合使用饼图展示比例关系'
            })
        
        return recommendations[:7]  # 最多返回7种推荐
    
    def generate_visualizations(self, data: pd.DataFrame, 
                               visualization_config: Dict) -> Dict[str, Figure]:
        """
        根据配置生成多个可视化图表
        
        Args:
            data: 数据框
            visualization_config: 可视化配置字典
            
        Returns:
            图表名称到图表对象的映射
        """
        charts = {}
        
        # 生成基础统计图表
        if visualization_config.get('basic_stats', True):
            # 为数值列生成直方图
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            for col in numeric_cols[:3]:  # 限制显示数量
                chart_name = f"直方图_{col}"
                charts[chart_name] = self.visualizer.create_histogram(
                    data, col, title=f"{col}的分布")
            
            # 相关性热力图
            if len(numeric_cols) > 1:
                chart_name = "相关性热力图"
                charts[chart_name] = self.visualizer.create_heatmap(
                    data, title="特征相关性热力图")
        
        # 生成特定类型的图表
        if 'chart_types' in visualization_config:
            for chart_type, params in visualization_config['chart_types'].items():
                try:
                    if chart_type == 'bar':
                        charts[f"柱状图_{params['y_column']}"] = self.visualizer.create_bar_chart(
                            data, **params)
                    elif chart_type == 'line':
                        charts[f"折线图_{params['y_columns']}"] = self.visualizer.create_line_chart(
                            data, **params)
                    elif chart_type == 'scatter':
                        charts[f"散点图_{params['x_column']}_{params['y_column']}"] = self.visualizer.create_scatter_plot(
                            data, **params)
                    elif chart_type == 'box':
                        charts[f"箱线图_{params['y_column']}"] = self.visualizer.create_box_plot(
                            data, **params)
                    elif chart_type == 'pie':
                        charts["饼图"] = self.visualizer.create_pie_chart(
                            data, **params)
                except Exception as e:
                    print(f"创建{chart_type}图表时出错: {e}")
        
        self.created_charts = charts
        return charts
    
    def get_recommended_charts(self, data: pd.DataFrame, 
                              data_features: Dict) -> Dict[str, Figure]:
        """
        根据数据特征自动推荐并生成合适的图表
        
        Args:
            data: 数据框
            data_features: 数据特征字典
            
        Returns:
            推荐的图表
        """
        charts = {}
        visualizer = self.visualizer
        
        # 基本推荐规则
        numeric_cols = data_features.get('numeric_columns', [])
        categorical_cols = data_features.get('categorical_columns', [])
        
        # 1. 数值列分布直方图
        if numeric_cols:
            for col in numeric_cols[:2]:  # 最多显示2个
                charts[f"histogram_{col}"] = visualizer.create_histogram(
                    data, col, title=f"{col}的分布")
        
        # 2. 数值列之间的散点图（如果有多个数值列）
        if len(numeric_cols) >= 2:
            charts["scatter_relationship"] = visualizer.create_scatter_plot(
                data, numeric_cols[0], numeric_cols[1],
                title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                trendline=True
            )
        
        # 3. 相关性热力图
        if len(numeric_cols) >= 3:
            charts["correlation_heatmap"] = visualizer.create_heatmap(
                data, title="特征相关性热力图")
        
        # 4. 分类列的箱线图
        if categorical_cols and numeric_cols:
            for cat_col in categorical_cols[:1]:  # 最多1个分类列
                for num_col in numeric_cols[:2]:  # 最多2个数值列
                    charts[f"boxplot_{cat_col}_{num_col}"] = visualizer.create_box_plot(
                        data, cat_col, num_col,
                        title=f"{num_col}在{cat_col}各水平下的分布")
        
        # 5. 分类列的饼图
        if categorical_cols:
            for cat_col in categorical_cols[:1]:  # 最多1个分类列
                # 计算频率
                freq_data = data[cat_col].value_counts().reset_index()
                freq_data.columns = [cat_col, 'count']
                
                charts[f"pie_{cat_col}"] = visualizer.create_pie_chart(
                    freq_data, 'count', cat_col,
                    title=f"{cat_col}的分布")
        
        # 6. 如果有时间列，创建时间序列图
        date_cols = data_features.get('date_columns', [])
        if date_cols and numeric_cols:
            for date_col in date_cols[:1]:
                for num_col in numeric_cols[:1]:
                    # 按日期聚合
                    if data[date_col].dtype == 'datetime64[ns]':
                        time_data = data.groupby(data[date_col].dt.date)[num_col].mean().reset_index()
                        charts[f"time_series_{date_col}_{num_col}"] = visualizer.create_line_chart(
                            time_data, date_col, num_col,
                            title=f"{num_col}随{date_col}的变化趋势")
        
        return charts
    
    def save_chart(self, chart_name: str, filepath: str, dpi: int = 300) -> bool:
        """
        保存指定名称的图表到文件
        
        Args:
            chart_name: 图表名称
            filepath: 文件路径
            dpi: 分辨率
            
        Returns:
            是否保存成功
        """
        if chart_name in self.created_charts:
            try:
                self.created_charts[chart_name].savefig(filepath, dpi=dpi, bbox_inches='tight')
                return True
            except Exception as e:
                print(f"保存图表失败: {e}")
                return False
        return False

# 创建工厂函数
def create_visualizer() -> DataVisualizer:
    """
    创建数据可视化器实例
    """
    return DataVisualizer()

def create_visualization_manager() -> VisualizationManager:
    """
    创建可视化管理器实例
    """
    return VisualizationManager()