"""
数据加载器模块 - 支持多种文件格式导入

支持的文件格式：
- CSV (.csv)
- Excel (.xlsx, .xls)
- JSON (.json)
- TXT (.txt)
- Parquet (.parquet)
"""

import os
import pandas as pd
import json
from pathlib import Path
import logging
from typing import Union, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DataLoader:
    """数据加载器类，负责从各种格式文件中加载数据"""
    
    # 支持的文件格式及其对应的读取函数
    SUPPORTED_FORMATS = {
        '.csv': 'read_csv',
        '.xlsx': 'read_excel',
        '.xls': 'read_excel',
        '.json': 'read_json',
        '.txt': 'read_csv',  # 假设txt文件是分隔符分隔的值
        '.parquet': 'read_parquet'
    }
    
    @staticmethod
    def get_supported_formats() -> list:
        """获取所有支持的文件格式列表"""
        return list(DataLoader.SUPPORTED_FORMATS.keys())
    
    @staticmethod
    def detect_file_format(file_path: Union[str, Path]) -> str:
        """检测文件格式"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext
    
    @staticmethod
    def is_supported_format(file_path: Union[str, Path]) -> bool:
        """检查文件格式是否支持"""
        file_ext = DataLoader.detect_file_format(file_path)
        return file_ext in DataLoader.SUPPORTED_FORMATS
    
    @staticmethod
    def load_data(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        加载数据文件
        
        Args:
            file_path: 文件路径
            **kwargs: 传递给pandas读取函数的参数
            
        Returns:
            pd.DataFrame: 加载的数据
            
        Raises:
            ValueError: 不支持的文件格式
            FileNotFoundError: 文件不存在
            Exception: 其他加载错误
        """
        file_path = Path(file_path)
        
        # 检查文件是否存在
        if not file_path.exists():
            error_msg = f"文件不存在: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # 检查文件格式
        file_ext = DataLoader.detect_file_format(file_path)
        if file_ext not in DataLoader.SUPPORTED_FORMATS:
            error_msg = f"不支持的文件格式: {file_ext}。支持的格式: {', '.join(DataLoader.SUPPORTED_FORMATS.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            logger.info(f"开始加载文件: {file_path.name}, 格式: {file_ext}")

            # 根据文件格式选择合适的读取函数
            read_func_name = DataLoader.SUPPORTED_FORMATS[file_ext]

            # 特殊处理不同格式以提高兼容性并提供更有用的错误信息
            if file_ext == '.txt':
                # 自动检测分隔符；使用 engine='python' 可提高 sep=None 的自动检测稳定性
                kwargs.setdefault('sep', None)
                kwargs.setdefault('engine', 'python')
                df = pd.read_csv(file_path, **kwargs)

            elif file_ext in ('.xlsx', '.xls'):
                # 优先尝试 pandas.read_excel 默认引擎；若失败，尝试指定 openpyxl 引擎并提示安装依赖
                try:
                    df = pd.read_excel(file_path, **kwargs)
                except Exception as e_excel:
                    # 如果是因为缺少 openpyxl 导致的错误，给出明确提示
                    if 'openpyxl' in str(e_excel) or 'Excel' in str(e_excel):
                        try:
                            df = pd.read_excel(file_path, engine='openpyxl', **kwargs)
                        except ModuleNotFoundError as me:
                            raise ModuleNotFoundError("读取 Excel 文件需要安装 'openpyxl'（或合适的 Excel 引擎），请运行 pip install openpyxl") from me
                        except Exception:
                            raise
                    else:
                        raise

            elif file_ext == '.json':
                # 先尝试普通 JSON，再尝试 lines=True（逐行 JSON）
                try:
                    df = pd.read_json(file_path, **kwargs)
                except ValueError:
                    try:
                        df = pd.read_json(file_path, lines=True, **kwargs)
                    except Exception as e_json:
                        raise Exception(f"读取 JSON 失败: {e_json}") from e_json

            elif file_ext == '.parquet':
                # parquet 需要 pyarrow 或 fastparquet
                try:
                    df = pd.read_parquet(file_path, **kwargs)
                except ModuleNotFoundError as me:
                    raise ModuleNotFoundError("读取 Parquet 文件需要安装 'pyarrow' 或 'fastparquet'，请运行 pip install pyarrow 或 pip install fastparquet") from me
                except Exception as e_parq:
                    raise

            else:
                # 其它格式（如 csv）使用对应 pandas 读取函数
                read_func = getattr(pd, read_func_name)
                df = read_func(file_path, **kwargs)

            logger.info(f"文件加载成功: {file_path.name}, 行数: {len(df)}, 列数: {len(df.columns)}")
            return df

        except ModuleNotFoundError as me:
            # 更友好的提示，方便 UI 显示并指导用户安装依赖
            error_msg = f"文件加载失败（缺少依赖）: {file_path.name}，错误: {str(me)}"
            logger.error(error_msg, exc_info=True)
            raise
        except Exception as e:
            error_msg = f"文件加载失败: {file_path.name}, 错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    @staticmethod
    def load_data_with_progress(file_path: Union[str, Path], progress_callback=None, **kwargs) -> pd.DataFrame:
        """
        加载数据文件并支持进度回调
        
        Args:
            file_path: 文件路径
            progress_callback: 进度回调函数，接收一个0-100的进度值
            **kwargs: 传递给pandas读取函数的参数
            
        Returns:
            pd.DataFrame: 加载的数据
        """
        # 模拟进度更新
        if progress_callback:
            progress_callback(10)  # 开始加载
        
        try:
            # 实际加载数据
            df = DataLoader.load_data(file_path, **kwargs)
            
            if progress_callback:
                progress_callback(90)  # 加载完成
            
            return df
        finally:
            if progress_callback:
                progress_callback(100)  # 无论成功失败，都设置为100%


class DataValidator:
    """数据验证器类，负责验证加载的数据是否有效"""
    
    @staticmethod
    def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据有效性并返回数据信息
        
        Args:
            df: 要验证的数据框
            
        Returns:
            Dict: 数据验证结果和信息
        """
        # 基本信息
        info = {
            'valid': True,
            'n_rows': len(df),
            'n_columns': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'summary': df.describe(include='all').to_dict() if len(df) > 0 else {},
            'issues': []
        }
        
        # 检查是否为空
        if df.empty:
            info['valid'] = False
            info['issues'].append("数据框为空")
        
        # 检查是否有重复列名
        if df.columns.duplicated().any():
            info['issues'].append("存在重复列名")
        
        # 检查缺失值
        total_missing = df.isnull().sum().sum()
        if total_missing > 0:
            missing_percent = (total_missing / (len(df) * len(df.columns))) * 100
            info['missing_percent'] = missing_percent
            if missing_percent > 80:
                info['issues'].append(f"数据缺失严重，缺失率: {missing_percent:.1f}%")
        
        # 检查数据类型
        num_numeric_cols = len(df.select_dtypes(include=['number']).columns)
        if num_numeric_cols == 0 and len(df) > 0:
            info['issues'].append("数据中没有数值型列，可能不适合数值分析")
        
        logger.info(f"数据验证完成: {info['n_rows']}行, {info['n_columns']}列, 有效: {info['valid']}")
        return info