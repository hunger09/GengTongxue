import os
import numpy as np
import pandas as pd
import pytest

from src.utils.file_io import load_data, extract_numeric
from src.analyzers.digit_dist import DigitDistributionAnalyzer
from src.analyzers.arithmetic import ArithmeticSequenceAnalyzer
from src.analyzers.duplicate import DuplicateDataAnalyzer
from src.analyzers.precision import PrecisionConsistencyAnalyzer
from src.analyzers.stddev import StandardDeviationAnalyzer
from src.analyzers.correlation import HighCorrelationAnalyzer

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

ALL_ANALYZERS = [
    (DigitDistributionAnalyzer(), False),
    (ArithmeticSequenceAnalyzer(), True),
    (DuplicateDataAnalyzer(), False),
    (PrecisionConsistencyAnalyzer(), False),
    (StandardDeviationAnalyzer(), True),
    (HighCorrelationAnalyzer(), True),
]


def run_all_analyzers(df: pd.DataFrame) -> list[tuple]:
    """模拟 main_window 的检测流程，返回全部可疑点。"""
    numeric_df = df.select_dtypes(include=[np.number])
    all_values = extract_numeric(df)
    if len(all_values) == 0:
        return []

    results = []
    for analyzer, needs_df in ALL_ANALYZERS:
        data = numeric_df if needs_df else all_values
        results.extend(analyzer.analyze(data))
    return results


class TestIntegration:

    def test_clean_file_no_findings(self):
        """clean_data.xlsx 应不触发任何告警。"""
        df = load_data(os.path.join(FIXTURES_DIR, "clean_data.xlsx"))
        results = run_all_analyzers(df)
        assert len(results) == 0, f"Clean data should have 0 findings, got {len(results)}: {results}"

    def test_suspicious_file_has_findings(self):
        """suspicious_data.xlsx 应触发至少 6 类告警。"""
        df = load_data(os.path.join(FIXTURES_DIR, "suspicious_data.xlsx"))
        results = run_all_analyzers(df)

        finding_types = {r[0] for r in results}
        expected_types = {
            "末位数字分布", "完美等差数列", "数据重复",
            "数据精度异常", "标准差异常", "强相关性",
        }

        missing = expected_types - finding_types
        assert len(missing) == 0, f"Missing expected findings: {missing}"
        assert len(results) >= 6
