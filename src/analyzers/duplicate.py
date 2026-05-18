import numpy as np
from collections import Counter

from .base import BaseAnalyzer


class DuplicateDataAnalyzer(BaseAnalyzer):
    """检测完全重复的数据 — 重复占比超过 5%。"""

    DUPLICATE_RATIO_THRESHOLD = 0.05
    SEVERE_RATIO_THRESHOLD = 0.2

    def analyze(self, values: np.ndarray) -> list[tuple]:
        value_counts = Counter(values)
        duplicates = [(v, c) for v, c in value_counts.items() if c > 1]

        if not duplicates:
            return []

        total_duplicates = sum(c for _, c in duplicates)
        duplicate_ratio = total_duplicates / len(values)

        if duplicate_ratio > self.DUPLICATE_RATIO_THRESHOLD:
            top_duplicates = sorted(duplicates, key=lambda x: x[1], reverse=True)[:5]
            top_str = ", ".join([f"{v:.4f}({c}次)" for v, c in top_duplicates])

            severity = "⭐⭐⭐⭐⭐" if duplicate_ratio > self.SEVERE_RATIO_THRESHOLD else "⭐⭐⭐⭐"
            return [(
                "数据重复",
                "全局",
                f"重复数据占比 {duplicate_ratio:.1%}，最高重复: {top_str}",
                severity
            )]
        return []
