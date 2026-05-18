import numpy as np
from collections import Counter

from .base import BaseAnalyzer


class PrecisionConsistencyAnalyzer(BaseAnalyzer):
    """检测数据精度一致性 — 大部分 1 位小数但存在集中末位的 2 位小数。"""

    def analyze(self, values: np.ndarray) -> list[tuple]:
        decimal_places = []
        for v in values:
            s = "{:.10f}".format(v).rstrip('0')
            dp = len(s.split('.')[1]) if '.' in s else 0
            decimal_places.append(dp)

        dp_counts = Counter(decimal_places)
        most_common_dp, most_common_count = dp_counts.most_common(1)[0]
        total = len(decimal_places)

        if most_common_dp == 1 and dp_counts.get(2, 0) > total * 0.1:
            two_dp_values = [v for v, dp in zip(values, decimal_places) if dp == 2]
            if two_dp_values:
                last_digits = [int(("{:.2f}".format(v))[-1]) for v in two_dp_values]
                ld_counts = Counter(last_digits)
                top_ld, top_count = ld_counts.most_common(1)[0]

                if top_count / len(two_dp_values) > 0.7:
                    return [(
                        "数据精度异常",
                        "全局",
                        f"大部分数据为1位小数，但{len(two_dp_values)}个数据为2位小数，且末位{top_ld}占比{top_count / len(two_dp_values):.1%}",
                        "⭐⭐⭐⭐"
                    )]
        return []
