import numpy as np
import pandas as pd

from .base import BaseAnalyzer


class HighCorrelationAnalyzer(BaseAnalyzer):
    """检测列之间的强相关性 — Pearson 相关系数 > 0.99。"""

    CORR_THRESHOLD = 0.99

    def analyze(self, df: pd.DataFrame) -> list[tuple]:
        if df.shape[1] < 2:
            return []

        results = []
        corr_matrix = df.corr()

        for i in range(corr_matrix.shape[0]):
            for j in range(i + 1, corr_matrix.shape[1]):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > self.CORR_THRESHOLD and not np.isnan(corr):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    results.append((
                        "强相关性",
                        f"列 {col1} 与 {col2}",
                        f"两列数据相关系数高达 {corr:.6f}，可能存在数据复制",
                        "⭐⭐⭐⭐"
                    ))
        return results
