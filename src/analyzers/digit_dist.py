import numpy as np
from scipy import stats
from collections import Counter

from .base import BaseAnalyzer


class DigitDistributionAnalyzer(BaseAnalyzer):
    """检测末位数字分布异常 — 卡方检验均匀性。"""

    def analyze(self, values: np.ndarray) -> list[tuple]:
        last_digits = []
        for v in values:
            s = "{:.10f}".format(v).rstrip('0').rstrip('.') if '.' in "{:.10f}".format(v) else str(int(v))
            if s:
                last_digits.append(int(s[-1]))

        if not last_digits:
            return []

        digit_counts = Counter(last_digits)
        total = len(last_digits)
        expected = total / 10

        chi_squared = sum((count - expected) ** 2 / expected for count in digit_counts.values())
        p_value = 1 - stats.chi2.cdf(chi_squared, 9)

        if p_value < 0.05:
            anomalies = []
            for digit in range(10):
                count = digit_counts.get(digit, 0)
                if count > expected * 2 or count < expected * 0.2:
                    anomalies.append(f"{digit}({count}次)")

            if anomalies:
                return [(
                    "末位数字分布",
                    "全局",
                    f"末位数字分布显著不均匀(p={p_value:.4f})，异常数字: {', '.join(anomalies)}",
                    "⭐⭐⭐⭐⭐"
                )]
        return []
