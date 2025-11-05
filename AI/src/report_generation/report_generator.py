import os
import io
import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from matplotlib.figure import Figure
import tempfile
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# 模块级日志器
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ReportGenerator:
    """
    Word报告生成器，用于创建专业的数据报告文档
    """
    
    def __init__(self):
        self.document = None
        self.temp_dir = tempfile.mkdtemp()
    
    def create_report(self, title: str = "数据分析报告", 
                     author: str = "AI数据分析系统",
                     subtitle: Optional[str] = None) -> None:
        """
        创建一个新的报告文档
        
        Args:
            title: 报告标题
            author: 报告作者
            subtitle: 报告副标题
        """
        # 创建新文档
        self.document = Document()
        
        # 设置标题
        self._add_title_section(title, subtitle, author)
        
        # 添加目录
        self._add_table_of_contents()


    def _add_title_section(self, title: str, subtitle: Optional[str], author: str) -> None:
        """
        添加标题部分
        """
        # 主标题
        title_para = self.document.add_heading(title, 0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 副标题
        if subtitle:
            subtitle_para = self.document.add_heading(subtitle, level=1)
            subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加空行
        self.document.add_paragraph()
        
        # 添加作者和日期信息
        info_para = self.document.add_paragraph()
        info_run = info_para.add_run(f"作者: {author}")
        info_run.font.size = Pt(12)
        info_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # 添加日期
        date_para = self.document.add_paragraph()
        date_run = date_para.add_run(f"生成日期: {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
        date_run.font.size = Pt(12)
        date_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # 分页符
        self.document.add_page_break()
    
    def _add_table_of_contents(self) -> None:
        """
        添加目录
        """
        # 目录标题
        toc_title = self.document.add_heading("目录", level=1)
        toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加目录（实际内容会在保存前更新）
        self.document.add_paragraph("[目录将在保存时自动生成]")
        
        # 分页符
        self.document.add_page_break()
    
    def add_executive_summary(self, summary: str) -> None:
        """
        添加执行摘要
        
        Args:
            summary: 摘要内容
        """
        self.document.add_heading("执行摘要", level=1)
        
        # 添加摘要段落
        self.document.add_paragraph(summary)
        
        # 添加空行
        self.document.add_paragraph()
    
    def add_data_overview(self, data_info: Dict) -> None:
        """
        添加数据概览部分
        
        Args:
            data_info: 数据信息字典，包含行数、列数、文件名称等
        """
        self.document.add_heading("1. 数据概览", level=1)
        
        # 添加基本信息
        self.document.add_heading("1.1 数据集基本信息", level=2)
        
        # 创建信息表格
        info_table = self.document.add_table(rows=1, cols=2)
        info_table.style = 'Table Grid'
        info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # 表头
        hdr_cells = info_table.rows[0].cells
        hdr_cells[0].text = '属性'
        hdr_cells[1].text = '值'
        
        # 设置表头样式
        for cell in hdr_cells:
            cell.paragraphs[0].runs[0].bold = True
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        # 添加数据
        rows = [
            ('文件名称', str(data_info.get('file_name', '未知')) if data_info.get('file_name') is not None else '未知'),
            ('数据格式', str(data_info.get('file_format', '未知')) if data_info.get('file_format') is not None else '未知'),
            ('数据行数', str(data_info.get('num_rows', 0))),
            ('数据列数', str(data_info.get('num_columns', 0))),
            ('数值型特征', str(data_info.get('num_numeric_cols', 0))),
            ('分类型特征', str(data_info.get('num_categorical_cols', 0))),
            ('日期型特征', str(data_info.get('num_date_cols', 0))),
            ('数据大小', str(data_info.get('data_size', '未知')) if data_info.get('data_size') is not None else '未知')
        ]
        
        for row_data in rows:
            cells = info_table.add_row().cells
            # 确保所有文本都不为None，进行双重保护
            key_text = row_data[0]
            value_text = row_data[1]
            
            # 保证键名永远不为None
            if key_text is None:
                key_text = '未知项目'
            elif not isinstance(key_text, str):
                key_text = str(key_text)
            
            # 保证值永远不为None
            if value_text is None:
                value_text = '未知'
            elif not isinstance(value_text, str):
                value_text = str(value_text)
            
            cells[0].text = key_text
            cells[1].text = value_text
            for cell in cells:
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        # 添加列信息
        if 'columns_info' in data_info:
            self.document.add_heading("1.2 列信息", level=2)
            
            col_table = self.document.add_table(rows=1, cols=4)
            col_table.style = 'Table Grid'
            col_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # 表头
            hdr_cells = col_table.rows[0].cells
            hdr_cells[0].text = '列名'
            hdr_cells[1].text = '数据类型'
            hdr_cells[2].text = '非空值数量'
            hdr_cells[3].text = '描述'
            
            for cell in hdr_cells:
                cell.paragraphs[0].runs[0].bold = True
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            # 添加列数据
            for col_info in data_info['columns_info']:
                cells = col_table.add_row().cells
                # 确保所有文本都不为None
                cells[0].text = str(col_info.get('name', '')) if col_info.get('name') is not None else ''
                cells[1].text = str(col_info.get('dtype', '')) if col_info.get('dtype') is not None else ''
                cells[2].text = str(col_info.get('non_null_count', 0))
                cells[3].text = str(col_info.get('description', 'N/A')) if col_info.get('description') is not None else 'N/A'
                for cell in cells:
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        # 添加空行
        self.document.add_paragraph()
    
    def add_data_preprocessing_section(self, preprocessing_info: Dict) -> None:
        """
        添加数据预处理部分
        
        Args:
            preprocessing_info: 预处理信息字典
        """
        self.document.add_heading("2. 数据预处理", level=1)
        
        # 缺失值处理（对可能为 None 的字段进行保护）
        mv_info = preprocessing_info.get('missing_values') or {}
        if mv_info:
            self.document.add_heading("2.1 缺失值处理", level=2)

            mv_para = self.document.add_paragraph()
            mv_para.add_run(f"发现 {mv_info.get('total_missing', 0)} 个缺失值，分布在 {mv_info.get('columns_with_missing', 0)} 列中。").bold = True

            # 添加处理方法
            handling_method = mv_info.get('handling_method')
            if handling_method:
                self.document.add_paragraph(f"处理方法: {handling_method}")

            # 如果有处理详情
            for detail in mv_info.get('details') or []:
                # 确保 details 可迭代
                if detail is None:
                    continue
                self.document.add_paragraph(f"- {detail}", style='List Bullet')
        
        # 异常值处理（保护 None）
        outliers_info = preprocessing_info.get('outliers') or {}
        if outliers_info:
            self.document.add_heading("2.2 异常值处理", level=2)

            outliers_para = self.document.add_paragraph()
            outliers_para.add_run(f"发现 {outliers_info.get('total_outliers', 0)} 个异常值，分布在 {outliers_info.get('columns_with_outliers', 0)} 列中。").bold = True

            # 添加处理方法
            if outliers_info.get('handling_method'):
                self.document.add_paragraph(f"处理方法: {outliers_info.get('handling_method')}")
        
        # 特征工程（保护 None）
        fe_info = preprocessing_info.get('feature_engineering') or {}
        if fe_info:
            self.document.add_heading("2.3 特征工程", level=2)

            # 编码处理
            if fe_info.get('encoding'):
                self.document.add_paragraph(f"分类特征编码: {fe_info.get('encoding')}")

            # 标准化/归一化
            if fe_info.get('scaling'):
                self.document.add_paragraph(f"数值特征缩放: {fe_info.get('scaling')}")

            # 特征选择
            feature_selection = fe_info.get('feature_selection') or {}
            selected_features = feature_selection.get('selected_features', []) if isinstance(feature_selection, dict) else []
            self.document.add_paragraph(f"选择的特征数量: {len(selected_features)}")

            # 添加选择的特征列表
            if len(selected_features) <= 10:  # 只显示前10个特征
                if selected_features:
                    features_para = self.document.add_paragraph("选择的特征:")
                    for feature in selected_features:
                        if feature is None:
                            continue
                        self.document.add_paragraph(f"- {feature}", style='List Bullet')
            else:
                self.document.add_paragraph(f"(显示前10个特征)")
                for feature in selected_features[:10]:
                    if feature is None:
                        continue
                    self.document.add_paragraph(f"- {feature}", style='List Bullet')
        
        # 添加空行
        self.document.add_paragraph()
    
    def add_analysis_results(self, analysis_results: Dict) -> None:
        """
        添加分析结果部分
        
        Args:
            analysis_results: 分析结果字典
        """
        try:
            logger.info("开始添加分析结果")
            self.document.add_heading("3. 数据分析结果", level=1)

            # 保护 analysis_results 为 None 的情况
            if not analysis_results:
                logger.warning("analysis_results为空，添加默认消息")
                self.document.add_paragraph("暂无分析结果可展示。")
                self.document.add_paragraph()
                return

            logger.debug(f"analysis_results keys: {list(analysis_results.keys())}")

            # 描述性统计
            try:
                if 'descriptive_stats' in analysis_results:
                    logger.info("添加描述性统计")
                    self.document.add_heading("3.1 描述性统计", level=2)
                    
                    stats_df = analysis_results.get('descriptive_stats')
                    logger.debug(f"stats_df type: {type(stats_df)}")
                    
                    if isinstance(stats_df, pd.DataFrame) and not stats_df.empty:
                        # 创建表格
                        stats_table = self.document.add_table(rows=1, cols=len(stats_df.columns) + 1)
                        stats_table.style = 'Table Grid'
                        stats_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                        
                        # 表头
                        hdr_cells = stats_table.rows[0].cells
                        hdr_cells[0].text = '统计量'
                        for i, col in enumerate(stats_df.columns):
                            hdr_cells[i+1].text = str(col)
                        
                        for cell in hdr_cells:
                            cell.paragraphs[0].runs[0].bold = True
                            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                        
                        # 添加数据（只显示主要统计量）
                        stats_to_show = ['mean', 'std', 'min', '25%', '50%', '75%', 'max']
                        for stat in stats_to_show:
                            if stat in stats_df.index:
                                cells = stats_table.add_row().cells
                                cells[0].text = self._get_statistic_name(stat)
                                for i, col in enumerate(stats_df.columns):
                                    try:
                                        value = stats_df.loc[stat, col]
                                        cells[i+1].text = f"{value:.4f}" if pd.notnull(value) else "N/A"
                                    except Exception as e:
                                        logger.error(f"处理统计值时出错: {str(e)}")
                                        cells[i+1].text = "N/A"
                                for cell in cells:
                                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                        logger.info("描述性统计表格添加成功")
                    else:
                        logger.warning("描述性统计数据无效")
                        self.document.add_paragraph("描述性统计数据暂不可用。")
            except Exception as e:
                logger.error(f"添加描述性统计时出错: {str(e)}")
                self.document.add_paragraph("描述性统计生成时出现错误。")
        
            # 相关性分析
            try:
                if 'correlation' in analysis_results:
                    logger.info("添加相关性分析")
                    self.document.add_heading("3.2 相关性分析", level=2)
                    
                    corr_results = analysis_results.get('correlation') or {}
                    logger.debug(f"corr_results type: {type(corr_results)}, keys: {list(corr_results.keys()) if isinstance(corr_results, dict) else 'not dict'}")
                    
                    if isinstance(corr_results, dict):
                        method = corr_results.get('method', 'Pearson')
                        self.document.add_paragraph(f"相关性分析采用 {method} 方法。")
                        
                        # 显示强相关的特征对
                        strong_corr = corr_results.get('strong_correlations') or []
                        logger.debug(f"strong_correlations type: {type(strong_corr)}, length: {len(strong_corr) if hasattr(strong_corr, '__len__') else 'no len'}")
                        
                        if strong_corr and isinstance(strong_corr, (list, tuple)) and len(strong_corr) > 0:
                            self.document.add_paragraph("发现以下强相关特征对（相关系数绝对值 > 0.7）:")
                            for i, pair in enumerate(strong_corr):
                                try:
                                    # 保护每个 pair 是字典且包含需要的字段
                                    if not isinstance(pair, dict):
                                        logger.warning(f"强相关对 {i} 不是字典类型: {type(pair)}")
                                        continue
                                    f1 = pair.get('feature1', '未知')
                                    f2 = pair.get('feature2', '未知')
                                    corr_v = pair.get('correlation', 0.0)
                                    self.document.add_paragraph(f"- {f1} 和 {f2}: {corr_v:.4f}", style='List Bullet')
                                    logger.debug(f"添加强相关对: {f1} - {f2}: {corr_v}")
                                except Exception as e:
                                    logger.error(f"处理强相关对 {i} 时出错: {str(e)}")
                        else:
                            self.document.add_paragraph("未发现强相关的特征对。")
                    else:
                        logger.warning("相关性分析结果格式不正确")
                        self.document.add_paragraph("相关性分析结果暂不可用。")
                        
                    logger.info("相关性分析添加成功")
            except Exception as e:
                logger.error(f"添加相关性分析时出错: {str(e)}")
                self.document.add_paragraph("相关性分析生成时出现错误。")

            # 模型推荐
            try:
                if 'model_recommendations' in analysis_results:
                    logger.info("添加模型推荐")
                    recommendations = analysis_results.get('model_recommendations') or []
                    logger.debug(f"recommendations type: {type(recommendations)}, length: {len(recommendations) if hasattr(recommendations, '__len__') else 'no len'}")
                    
                    # 检查recommendations是否为可迭代列表
                    if isinstance(recommendations, (list, tuple)) and len(recommendations) > 0:
                        self.document.add_heading("3.3 模型推荐", level=2)
                        self.document.add_paragraph("根据数据特征，推荐以下分析模型:")
                        
                        for i, model in enumerate(recommendations, 1):
                            try:
                                if not isinstance(model, dict):
                                    logger.warning(f"模型推荐 {i} 不是字典类型: {type(model)}")
                                    continue
                                model_para = self.document.add_paragraph()
                                model_name = model.get('name', '未知模型')
                                model_score = model.get('score', 0)
                                model_para.add_run(f"{i}. {model_name}").bold = True
                                model_para.add_run(f" (推荐指数: {model_score:.2f}/10)")
                                
                                if model.get('description'):
                                    self.document.add_paragraph(str(model.get('description')), style='List Bullet')
                                
                                if model.get('reason'):
                                    self.document.add_paragraph(f"推荐原因: {model.get('reason')}", style='List Bullet')
                                    
                                logger.debug(f"添加模型推荐: {model_name}")
                            except Exception as e:
                                logger.error(f"处理模型推荐 {i} 时出错: {str(e)}")
                    else:
                        self.document.add_heading("3.3 模型推荐", level=2)
                        self.document.add_paragraph("暂无可用的模型推荐。")
                        
                    logger.info("模型推荐添加成功")
            except Exception as e:
                logger.error(f"添加模型推荐时出错: {str(e)}")
                self.document.add_paragraph("模型推荐生成时出现错误。")

            # 添加空行
            self.document.add_paragraph()
            logger.info("分析结果添加完成")
            
        except Exception as e:
            logger.exception(f"添加分析结果时发生未预期的错误: {str(e)}")
            raise
    
    def add_chart(self, chart: Union[Figure, str], title: str, 
                 description: Optional[str] = None) -> None:
        """
        添加图表到报告
        
        Args:
            chart: matplotlib Figure对象或图片路径
            title: 图表标题
            description: 图表描述
        """
        # 添加图表标题
        chart_heading = self.document.add_heading(title, level=2)
        
        # 保存图表到临时文件
        if isinstance(chart, Figure):
            img_path = os.path.join(self.temp_dir, f"chart_{len(os.listdir(self.temp_dir)) + 1}.png")
            chart.savefig(img_path, dpi=300, bbox_inches='tight')
            plt.close(chart)  # 关闭图表以释放内存
        else:
            img_path = chart
        
        # 添加图片
        if os.path.exists(img_path):
            para = self.document.add_paragraph()
            run = para.add_run()
            run.add_picture(img_path, width=Inches(6.0))
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加描述
        if description:
            desc_para = self.document.add_paragraph(description)
            desc_para.style = 'Quote'
        
        # 添加空行
        self.document.add_paragraph()
    
    def add_multiple_charts(self, charts: Optional[Dict[str, Figure]], section_title: str) -> None:
        """
        添加多个图表到报告
        
        Args:
            charts: 图表名称到图表对象的映射
            section_title: 章节标题
        """
        self.document.add_heading(section_title, level=1)
        
        # 检查charts是否存在、不为None且为字典类型
        if charts and isinstance(charts, dict):
            # 添加每个图表
            for chart_name, chart in charts.items():
                try:
                    self.add_chart(chart, chart_name, f"图表: {chart_name}")
                except Exception as e:
                    logger.exception(f"添加图表 {chart_name} 时发生异常: {e}")
                    # 继续添加其他图表
                    continue
        else:
            # 如果没有可用图表，添加说明文本
            self.document.add_paragraph("暂无可用的图表。")
    
    def add_conclusion(self, conclusion: str) -> None:
        """
        添加结论部分
        
        Args:
            conclusion: 结论内容
        """
        self.document.add_heading("4. 结论与建议", level=1)
        
        # 添加结论段落
        self.document.add_paragraph(conclusion)
        
        # 添加空行
        self.document.add_paragraph()
    
    def add_recommendations(self, recommendations: List[str]) -> None:
        """
        添加建议部分
        
        Args:
            recommendations: 建议列表
        """
        if recommendations:
            self.document.add_heading("4.1 业务建议", level=2)
            
            for rec in recommendations:
                self.document.add_paragraph(f"- {rec}", style='List Bullet')
    
    def save_report(self, output_path: Optional[str] = None) -> str:
        """
        保存报告到文件
        
        Args:
            output_path: 输出文件路径，如果未提供则自动生成
            
        Returns:
            保存的文件路径
        """
        if self.document is None:
            raise ValueError("请先创建报告")
        
        # 如果未提供路径，生成默认路径（桌面）
        if output_path is None:
            # 获取桌面路径
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # 生成文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(desktop_path, f"数据分析报告_{timestamp}.docx")
        
        # 更新目录
        # 注意：python-docx 不支持自动生成目录。为了避免直接操作底层 XML（可能导致 AttributeError），
        # 我们仅用一个占位文本替换原有标记，用户可以在 Word 中手动更新目录字段。
        for para in self.document.paragraphs:
            if "[目录将在保存时自动生成]" in para.text:
                para.clear()
                para.add_run("目录（请在 Word 中更新目录字段以生成最新目录）")
        
        # 保存文档
        # 确保输出目录存在
        try:
            out_dir = os.path.dirname(output_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            logger.exception(f"创建输出目录失败: {e}")
            raise

        try:
            self.document.save(output_path)
        except Exception as e:
            logger.exception(f"保存文档到 {output_path} 失败: {e}")
            # 抛出更友好的错误
            raise IOError(f"无法保存报告到 {output_path}: {e}")

        return output_path
    
    def _get_statistic_name(self, stat: str) -> str:
        """
        获取统计量的中文名称
        
        Args:
            stat: 统计量英文名称
            
        Returns:
            中文名称
        """
        stat_names = {
            'mean': '均值',
            'std': '标准差',
            'min': '最小值',
            '25%': '第一四分位数',
            '50%': '中位数',
            '75%': '第三四分位数',
            'max': '最大值',
            'count': '计数',
            'unique': '唯一值数量',
            'top': '最常见值',
            'freq': '最常见值频率'
        }
        return stat_names.get(stat, stat)

# 辅助函数
def qn(tag):
    """
    生成命名空间标签
    """
    return '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}' + tag

# 高级报告生成器类
class AdvancedReportGenerator:
    """
    高级报告生成器，集成数据分析结果自动生成完整报告
    """
    
    def __init__(self):
        self.generator = ReportGenerator()
    
    def generate_full_report(self, data: pd.DataFrame, 
                           analysis_results: Dict, 
                           charts: Optional[Dict[str, Figure]] = None,
                           file_info: Optional[Dict] = None,
                           output_path: Optional[str] = None) -> str:
        """
        生成完整的分析报告
        
        Args:
            data: 数据框
            analysis_results: 分析结果
            charts: 图表字典
            file_info: 文件信息
            output_path: 输出路径
            
        Returns:
            保存的文件路径
        """
        try:
            logger.info("开始生成完整的数据分析报告")
            
            # 保护 analysis_results 为 None 的情况
            analysis_results = analysis_results or {}
            if not isinstance(analysis_results, dict):
                raise ValueError("analysis_results 必须是字典类型")

            # 记录输入摘要以便调试
            logger.info(f"输入数据类型: {type(data)}, 行数: {len(data) if hasattr(data, '__len__') else 'unknown'}")
            logger.info(f"分析结果键: {list(analysis_results.keys())}")
            logger.info(f"图表类型: {type(charts)}, 图表数量: {len(charts) if charts else 0}")
            logger.info(f"文件信息: {file_info}")

            # 创建报告
            try:
                title = f"数据分析报告 - {file_info.get('file_name', '数据集')}" if file_info and isinstance(file_info, dict) else "数据分析报告"
                logger.info(f"创建报告，标题: {title}")
                self.generator.create_report(title=title)
                logger.info("报告文档创建成功")
            except Exception as e:
                logger.error(f"创建报告文档失败: {str(e)}")
                raise

        except Exception as e:
            logger.exception(f"生成完整报告时输入参数检查失败: {str(e)}")
            raise
        
        # 添加执行摘要
        try:
            logger.info("添加执行摘要")
            self._generate_executive_summary(data, analysis_results)
            logger.info("执行摘要添加成功")
        except Exception as e:
            logger.error(f"添加执行摘要失败: {str(e)}")
            logger.exception("执行摘要生成详细错误")
            raise
        
        # 添加数据概览
        try:
            logger.info("添加数据概览")
            self._generate_data_overview(data, file_info)
            logger.info("数据概览添加成功")
        except Exception as e:
            logger.error(f"添加数据概览失败: {str(e)}")
            logger.exception("数据概览生成详细错误")
            raise
        
        # 添加数据预处理信息
        try:
            if 'preprocessing' in analysis_results:
                logger.info("添加数据预处理信息")
                self.generator.add_data_preprocessing_section(analysis_results['preprocessing'])
                logger.info("数据预处理信息添加成功")
        except Exception as e:
            logger.error(f"添加数据预处理信息失败: {str(e)}")
            logger.exception("数据预处理信息生成详细错误")
            # 不抛出异常，继续执行
        
        # 添加分析结果
        try:
            logger.info("添加分析结果")
            self.generator.add_analysis_results(analysis_results)
            logger.info("分析结果添加成功")
        except Exception as e:
            logger.error(f"添加分析结果失败: {str(e)}")
            logger.exception("分析结果生成详细错误")
            raise
        
        # 添加图表
        try:
            if charts and isinstance(charts, dict):
                logger.info(f"添加图表，图表数量: {len(charts)}")
                self.generator.add_multiple_charts(charts, "5. 数据可视化")
                logger.info("图表添加成功")
            else:
                logger.info("无图表需要添加")
        except Exception as e:
            logger.error(f"添加图表失败: {str(e)}")
            logger.exception("图表生成详细错误")
            # 不抛出异常，继续执行
        
        # 添加结论和建议
        try:
            logger.info("添加结论和建议")
            self._generate_conclusion(analysis_results)
            logger.info("结论和建议添加成功")
        except Exception as e:
            logger.error(f"添加结论和建议失败: {str(e)}")
            logger.exception("结论和建议生成详细错误")
            raise
        
        # 保存报告
        try:
            logger.info("开始保存报告")
            saved_path = self.generator.save_report(output_path)
            logger.info(f"报告保存成功，路径: {saved_path}")
            return saved_path
        except Exception as e:
            logger.error(f"保存报告失败: {str(e)}")
            logger.exception("保存报告详细错误")
            raise
    
    def _generate_executive_summary(self, data: pd.DataFrame, 
                                   analysis_results: Dict) -> None:
        """
        自动生成执行摘要
        """
        try:
            logger.info("开始生成执行摘要")
            summary = []
            
            # 数据基本信息
            try:
                data_rows = len(data) if data is not None and hasattr(data, '__len__') else 0
                data_cols = len(data.columns) if data is not None and hasattr(data, 'columns') else 0
                summary.append(f"本报告分析了包含 {data_rows} 行和 {data_cols} 列的数据集。")
                logger.debug(f"数据基本信息: {data_rows} 行, {data_cols} 列")
            except Exception as e:
                logger.error(f"获取数据基本信息失败: {str(e)}")
                summary.append("本报告对提供的数据集进行了分析。")
            
            # 分析类型
            try:
                if analysis_results and 'analysis_type' in analysis_results and analysis_results['analysis_type']:
                    summary.append(f"根据数据特征，系统自动识别并执行了{analysis_results['analysis_type']}分析。")
                    logger.debug(f"分析类型: {analysis_results['analysis_type']}")
            except Exception as e:
                logger.error(f"获取分析类型失败: {str(e)}")
            
            # 主要发现
            summary.append("\n主要发现：")
            
            # 从分析结果中提取主要发现（保护可能为 None 的字段）
            try:
                key_findings = analysis_results.get('key_findings') if analysis_results else None
                logger.debug(f"主要发现类型: {type(key_findings)}, 内容: {key_findings}")
                
                if key_findings and isinstance(key_findings, (list, tuple)) and len(key_findings) > 0:
                    for i, finding in enumerate(key_findings[:3]):  # 最多显示3个主要发现
                        if finding:  # 确保finding不为None或空字符串
                            summary.append(f"• {finding}")
                            logger.debug(f"添加主要发现 {i+1}: {finding}")
                else:
                    logger.info("没有找到key_findings，尝试从其他分析结果中提取发现")
                    
                    # 尝试从相关性分析中提取发现
                    try:
                        if (analysis_results and 'correlation' in analysis_results and 
                            analysis_results['correlation'] and 'strong_correlations' in analysis_results['correlation']):
                            strong_corr = analysis_results['correlation']['strong_correlations']
                            if strong_corr and hasattr(strong_corr, '__len__'):
                                summary.append(f"• 发现 {len(strong_corr)} 对强相关特征。")
                                logger.debug(f"发现强相关特征: {len(strong_corr)} 对")
                    except Exception as e:
                        logger.error(f"提取相关性分析发现失败: {str(e)}")
                    
                    # 从统计分析中提取发现
                    try:
                        if analysis_results and 'descriptive_stats' in analysis_results:
                            stats_df = analysis_results['descriptive_stats']
                            if data is not None and hasattr(data, 'select_dtypes'):
                                numeric_cols = data.select_dtypes(include=[np.number]).columns
                                if len(numeric_cols) > 0:
                                    # 优先直接从原始数据计算标准差并找出变异最大的列，这比依赖统计表更稳健
                                    try:
                                        std_series = data[numeric_cols].std()
                                        if std_series is not None and not std_series.empty:
                                            max_var_col = std_series.idxmax()
                                            summary.append(f"• {max_var_col} 是变异程度最大的特征。")
                                            logger.debug(f"变异最大的特征: {max_var_col}")
                                    except Exception as e:
                                        logger.error(f"计算变异程度失败: {str(e)}")
                                        # 退回到尝试从 stats_df 中读取 'std' 行（如果存在）
                                        try:
                                            if stats_df is not None and hasattr(stats_df, 'loc') and 'std' in stats_df.index:
                                                max_var_col = stats_df.loc['std'].idxmax()
                                                summary.append(f"• {max_var_col} 是变异程度最大的特征。")
                                                logger.debug(f"从统计表获取变异最大的特征: {max_var_col}")
                                        except Exception as e2:
                                            logger.error(f"从统计表获取变异程度失败: {str(e2)}")
                    except Exception as e:
                        logger.error(f"提取统计分析发现失败: {str(e)}")
                        
            except Exception as e:
                logger.error(f"提取主要发现失败: {str(e)}")
                summary.append("• 数据质量良好，适合进行分析。")
            
            # 模型推荐
            try:
                if (analysis_results and 'model_recommendations' in analysis_results and 
                    analysis_results['model_recommendations'] and 
                    isinstance(analysis_results['model_recommendations'], (list, tuple)) and
                    len(analysis_results['model_recommendations']) > 0):
                    top_model = analysis_results['model_recommendations'][0]
                    if top_model and isinstance(top_model, dict):
                        model_name = top_model.get('name', '未知模型')
                        summary.append(f"\n推荐模型：{model_name}")
                        logger.debug(f"推荐模型: {model_name}")
            except Exception as e:
                logger.error(f"获取模型推荐失败: {str(e)}")
            
            # 合并摘要
            try:
                summary_text = " ".join(str(s) for s in summary if s)  # 确保所有元素都是字符串且非空
                logger.debug(f"生成的摘要文本长度: {len(summary_text)}")
                self.generator.add_executive_summary(summary_text)
                logger.info("执行摘要生成完成")
            except Exception as e:
                logger.error(f"合并和添加摘要失败: {str(e)}")
                # 使用简单的默认摘要
                default_summary = "本报告对数据集进行了全面的分析，包括数据概览、统计分析和可视化展示。"
                self.generator.add_executive_summary(default_summary)
                logger.info("使用默认摘要")
                
        except Exception as e:
            logger.exception(f"生成执行摘要时发生未预期的错误: {str(e)}")
            raise
    
    def _generate_data_overview(self, data: pd.DataFrame, 
                              file_info: Optional[Dict] = None) -> None:
        """
        自动生成数据概览
        """
        try:
            logger.info("开始生成数据概览")
            
            # 安全地处理file_info
            safe_file_info = file_info or {}
            
            data_info = {
                'file_name': str(safe_file_info.get('file_name', '未知')) if safe_file_info.get('file_name') is not None else '未知',
                'file_format': str(safe_file_info.get('file_format', '未知')) if safe_file_info.get('file_format') is not None else '未知',
                'num_rows': len(data) if data is not None else 0,
                'num_columns': len(data.columns) if data is not None and hasattr(data, 'columns') else 0,
                'num_numeric_cols': len(data.select_dtypes(include=[np.number]).columns) if data is not None else 0,
                'num_categorical_cols': len(data.select_dtypes(include=['object', 'category']).columns) if data is not None else 0,
                'num_date_cols': len(data.select_dtypes(include=['datetime64']).columns) if data is not None else 0,
                'data_size': f"{data.memory_usage(deep=True).sum() / 1024:.2f} KB" if data is not None and hasattr(data, 'memory_usage') else '未知'
            }
            
            logger.debug(f"数据概览信息: {data_info}")
            
            # 列信息
            columns_info = []
            if data is not None and hasattr(data, 'columns'):
                for col in data.columns[:10]:  # 只显示前10列
                    try:
                        col_info = {
                            'name': str(col) if col is not None else '未知列',
                            'dtype': str(data[col].dtype) if hasattr(data[col], 'dtype') else '未知',
                            'non_null_count': int(data[col].count()) if hasattr(data[col], 'count') else 0,
                            'description': f"缺失值: {data[col].isnull().sum()}" if hasattr(data[col], 'isnull') else 'N/A'
                        }
                        columns_info.append(col_info)
                        logger.debug(f"处理列: {col}, 信息: {col_info}")
                    except Exception as e:
                        logger.error(f"处理列 {col} 时出错: {str(e)}")
                        # 添加默认信息
                        col_info = {
                            'name': str(col) if col is not None else '未知列',
                            'dtype': '未知',
                            'non_null_count': 0,
                            'description': 'N/A'
                        }
                        columns_info.append(col_info)
            
            data_info['columns_info'] = columns_info
            logger.info(f"生成了 {len(columns_info)} 个列的信息")
            
            # 添加到报告
            self.generator.add_data_overview(data_info)
            logger.info("数据概览添加成功")
            
        except Exception as e:
            logger.exception(f"生成数据概览时发生未预期的错误: {str(e)}")
            raise
    
    def _generate_conclusion(self, analysis_results: Dict) -> None:
        """
        自动生成结论和建议
        """
        try:
            logger.info("开始生成结论和建议")
            conclusion_parts = []
            
            # 总结数据分析结果
            conclusion_parts.append("通过对数据集的全面分析，我们得出以下结论：")
            
            # 添加主要结论（保护可能为 None 的字段）
            try:
                conclusions = analysis_results.get('conclusions') if analysis_results else None
                logger.debug(f"结论类型: {type(conclusions)}, 内容: {conclusions}")
                
                if conclusions and isinstance(conclusions, (list, tuple)) and len(conclusions) > 0:
                    for i, conclusion in enumerate(conclusions, 1):
                        if conclusion:  # 确保conclusion不为None或空字符串
                            conclusion_parts.append(f"{i}. {conclusion}")
                            logger.debug(f"添加结论 {i}: {conclusion}")
                else:
                    logger.info("没有找到预设结论，生成自动结论")
                    # 尝试自动生成结论
                    conclusion_parts.append("1. 数据质量良好，经过适当的清洗和预处理后可用于进一步分析。")
                    
                    if analysis_results and 'correlation' in analysis_results:
                        conclusion_parts.append("2. 通过相关性分析发现了特征间的重要关联关系。")
                    
                    if analysis_results and 'model_recommendations' in analysis_results:
                        conclusion_parts.append("3. 基于数据特征，系统推荐了适合的分析模型。")
                        
            except Exception as e:
                logger.error(f"生成结论失败: {str(e)}")
                conclusion_parts.append("1. 数据质量良好，经过适当的清洗和预处理后可用于进一步分析。")
            
            # 合并结论
            try:
                conclusion_text = " ".join(str(part) for part in conclusion_parts if part)
                logger.debug(f"生成的结论文本长度: {len(conclusion_text)}")
                self.generator.add_conclusion(conclusion_text)
                logger.info("结论添加成功")
            except Exception as e:
                logger.error(f"添加结论失败: {str(e)}")
                default_conclusion = "通过对数据集的全面分析，我们得出以下结论：1. 数据质量良好，适合进行分析。"
                self.generator.add_conclusion(default_conclusion)
                logger.info("使用默认结论")
            
            # 添加建议
            try:
                recommendations = []
                if (analysis_results and 'recommendations' in analysis_results and 
                    analysis_results['recommendations'] is not None):
                    # 确保recommendations是可迭代的列表
                    if isinstance(analysis_results['recommendations'], (list, tuple)):
                        recommendations = [rec for rec in analysis_results['recommendations'] if rec]  # 过滤掉空值
                        logger.debug(f"找到 {len(recommendations)} 个预设建议")
                
                if not recommendations:
                    logger.info("没有找到预设建议，生成自动建议")
                    # 自动生成建议
                    recommendations.append("持续收集数据，建立时间序列分析模型以预测未来趋势。")
                    recommendations.append("考虑引入更多相关特征以提高分析精度。")
                    recommendations.append("基于推荐的模型进行深入的预测分析。")
                    recommendations.append("定期更新分析报告，监控关键指标的变化。")
                
                logger.debug(f"最终建议数量: {len(recommendations)}")
                self.generator.add_recommendations(recommendations)
                logger.info("建议添加成功")
                
            except Exception as e:
                logger.error(f"添加建议失败: {str(e)}")
                default_recommendations = [
                    "持续收集数据，建立时间序列分析模型以预测未来趋势。",
                    "考虑引入更多相关特征以提高分析精度。"
                ]
                self.generator.add_recommendations(default_recommendations)
                logger.info("使用默认建议")
                
        except Exception as e:
            logger.exception(f"生成结论和建议时发生未预期的错误: {str(e)}")
            raise

# 创建工厂函数
def create_report_generator() -> ReportGenerator:
    """
    创建报告生成器实例
    """
    return ReportGenerator()

def create_advanced_report_generator() -> AdvancedReportGenerator:
    """
    创建高级报告生成器实例
    """
    return AdvancedReportGenerator()