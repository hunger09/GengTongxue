import pandas as pd

from .base import BaseAnalyzer


class ArithmeticSequenceAnalyzer(BaseAnalyzer):
    """检测完美等差数列 — 连续 4+ 数据点差值完全相同。"""

    FLOAT_TOL = 1e-10

    def analyze(self, df: pd.DataFrame) -> list[tuple]:
        results = []
        for col_name, col_data in df.items():
            values = col_data.dropna().values
            if len(values) < 3:
                continue

            i = 0
            while i < len(values) - 2:
                diff1 = values[i + 1] - values[i]
                diff2 = values[i + 2] - values[i + 1]

                if abs(diff1 - diff2) < self.FLOAT_TOL and diff1 != 0:
                    seq_length = 3
                    j = i + 3
                    while j < len(values) and abs(values[j] - values[j - 1] - diff1) < self.FLOAT_TOL:
                        seq_length += 1
                        j += 1

                    if seq_length >= 4:
                        results.append((
                            "完美等差数列",
                            f"列 {col_name}, 行 {i + 1} 至 {j}",
                            f"发现长度为 {seq_length} 的完美等差数列，公差={diff1:.6f}",
                            "⭐⭐⭐⭐⭐"
                        ))
                        i = j  # 跳过已覆盖的位置
                        continue
                i += 1
        return results
