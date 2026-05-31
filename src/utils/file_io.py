import pandas as pd
import numpy as np


def load_data(file_path: str) -> pd.DataFrame:
    """加载 Excel 或 CSV 文件，返回 DataFrame。"""
    if file_path.endswith('.csv'):
        try:
            return pd.read_csv(file_path)
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding='gbk')
    return pd.read_excel(file_path)


def extract_numeric(df: pd.DataFrame) -> np.ndarray:
    """从 DataFrame 中提取所有数值型数据，返回扁平化的 1D 数组（去除 NaN）。"""
    numeric_df = df.select_dtypes(include=[np.number])
    values = numeric_df.values.flatten()
    return values[~np.isnan(values)]
