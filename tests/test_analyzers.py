import numpy as np
import pandas as pd
import pytest

from src.analyzers.digit_dist import DigitDistributionAnalyzer
from src.analyzers.arithmetic import ArithmeticSequenceAnalyzer
from src.analyzers.duplicate import DuplicateDataAnalyzer
from src.analyzers.precision import PrecisionConsistencyAnalyzer
from src.analyzers.stddev import StandardDeviationAnalyzer
from src.analyzers.correlation import HighCorrelationAnalyzer


# ── 末位数字分布 ──

class TestDigitDistribution:

    def test_positive(self):
        """末位集中在 0 和 5 的数据应被检出。"""
        values = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5,
                           6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5,
                           1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5])
        results = DigitDistributionAnalyzer().analyze(values)
        assert len(results) > 0
        assert results[0][0] == "末位数字分布"

    def test_negative(self):
        """均匀末位分布的数据不应被检出。"""
        # 构造末位 0-9 各出现 10 次
        values = np.array([float(d) + i * 10 for i in range(10) for d in range(10)])
        results = DigitDistributionAnalyzer().analyze(values)
        assert len(results) == 0


# ── 完美等差数列 ──

class TestArithmeticSequence:

    def test_positive(self):
        """完美等差数列 >= 4 项应被检出。"""
        df = pd.DataFrame({"col": list(range(1, 21))})
        results = ArithmeticSequenceAnalyzer().analyze(df)
        assert len(results) > 0
        assert results[0][0] == "完美等差数列"

    def test_negative(self):
        """非等差数据不应被检出。"""
        np.random.seed(42)
        df = pd.DataFrame({"col": np.round(np.random.normal(50, 15, 20), 1)})
        results = ArithmeticSequenceAnalyzer().analyze(df)
        assert len(results) == 0

    def test_short_sequence_ignored(self):
        """不足 4 项的等差不应被检出。"""
        df = pd.DataFrame({"col": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0, 5.0]})
        results = ArithmeticSequenceAnalyzer().analyze(df)
        assert len(results) == 0


# ── 重复数据 ──

class TestDuplicateData:

    def test_positive(self):
        """重复率 > 5% 应被检出。"""
        values = np.array([1.0] * 10 + [2.0] * 5 + [3.0] * 3 + [float(i) for i in range(4, 15)])
        results = DuplicateDataAnalyzer().analyze(values)
        assert len(results) > 0
        assert results[0][0] == "数据重复"

    def test_severe(self):
        """重复率 > 20% 应为 5 星。"""
        values = np.array([1.0] * 20 + [float(i) for i in range(2, 22)])
        results = DuplicateDataAnalyzer().analyze(values)
        assert len(results) > 0
        assert results[0][3] == "⭐⭐⭐⭐⭐"

    def test_negative(self):
        """无重复数据不应被检出。"""
        values = np.arange(1, 101, dtype=float)
        results = DuplicateDataAnalyzer().analyze(values)
        assert len(results) == 0


# ── 精度一致性 ──

class TestPrecisionConsistency:

    def test_positive(self):
        """大部分 1 位小数 + 部分 2 位小数末位集中应被检出。"""
        values = np.array([round(10.0 + i * 0.3, 1) for i in range(20)]
                          + [round(15.0 + i * 0.1, 2) - 0.03 for i in range(6, 16)])
        results = PrecisionConsistencyAnalyzer().analyze(values)
        assert len(results) > 0
        assert results[0][0] == "数据精度异常"

    def test_negative(self):
        """统一 1 位小数不应被检出。"""
        np.random.seed(42)
        values = np.round(np.random.normal(50, 15, 50), 1)
        results = PrecisionConsistencyAnalyzer().analyze(values)
        assert len(results) == 0


# ── 标准差异常 ──

class TestStandardDeviation:

    def test_positive_low_cv(self):
        """CV < 0.01 应被检出。"""
        df = pd.DataFrame({"col": [100.0 + np.random.uniform(-0.005, 0.005) for _ in range(30)]})
        results = StandardDeviationAnalyzer().analyze(df)
        assert len(results) > 0
        assert "⭐⭐⭐⭐" in results[0][3]

    def test_positive_high_cv(self):
        """CV > 1.0 应被检出。"""
        df = pd.DataFrame({"col": [1.0, 0.01, 50.0, 200.0, 0.05, 100.0, 500.0, 0.001,
                                     300.0, 10.0, 0.1, 150.0, 800.0, 0.02, 250.0, 5.0,
                                     0.5, 400.0, 0.03, 100.0]})
        results = StandardDeviationAnalyzer().analyze(df)
        assert len(results) > 0
        assert "⭐⭐⭐" in results[0][3]

    def test_negative(self):
        """正常 CV (0.01~1.0) 不应被检出。"""
        np.random.seed(42)
        df = pd.DataFrame({"col": np.round(np.random.normal(50, 15, 30), 1)})
        results = StandardDeviationAnalyzer().analyze(df)
        assert len(results) == 0


# ── 强相关性 ──

class TestHighCorrelation:

    def test_positive(self):
        """相关系数 > 0.99 应被检出。"""
        np.random.seed(42)
        base = np.random.normal(50, 10, 30)
        col_a = np.round(base, 1)
        col_b = np.round(base + np.random.uniform(-0.01, 0.01, 30), 1)
        df = pd.DataFrame({"a": col_a, "b": col_b})
        results = HighCorrelationAnalyzer().analyze(df)
        assert len(results) > 0
        assert results[0][0] == "强相关性"

    def test_negative(self):
        """低相关列不应被检出。"""
        np.random.seed(42)
        df = pd.DataFrame({
            "a": np.round(np.random.normal(50, 15, 30), 1),
            "b": np.round(np.random.normal(200, 40, 30), 1),
        })
        results = HighCorrelationAnalyzer().analyze(df)
        assert len(results) == 0

    def test_single_column_ignored(self):
        """单列数据不应报错或检出。"""
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
        results = HighCorrelationAnalyzer().analyze(df)
        assert len(results) == 0
