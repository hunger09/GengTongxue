import numpy as np
import pandas as pd

from .base import BaseAnalyzer


class StandardDeviationAnalyzer(BaseAnalyzer):
    """检测标准差异常 — 变异系数过低或过高。"""

    CV_LOW_THRESHOLD = 0.01
    CV_HIGH_THRESHOLD = 1.0

    def analyze(self, df: pd.DataFrame) -> list[tuple]:
        results = []
        for col_name, col_data in df.items():
            values = col_data.dropna().values
            if len(values) < 3:
                continue

            mean = np.mean(values)
            std = np.std(values)

            if mean == 0:
                continue

            cv = std / mean

            if cv < self.CV_LOW_THRESHOLD:
                results.append((
                    "标准差异常",
                    f"列 {col_name}",
                    f"变异系数仅为 {cv:.4f}，数据过于一致",
                    "⭐⭐⭐⭐"
                ))
            elif cv > self.CV_HIGH_THRESHOLD:
                results.append((
                    "标准差异常",
                    f"列 {col_name}",
                    f"变异系数为 {cv:.4f}，数据波动过大",
                    "⭐⭐⭐"
                ))
        return results
