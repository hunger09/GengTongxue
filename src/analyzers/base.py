from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """检测器基类，所有检测算法统一返回 (类型, 位置, 描述, 严重程度) 四元组列表。"""

    @abstractmethod
    def analyze(self, data):
        """
        执行检测分析。

        Args:
            data: 数值类检测接收 np.ndarray，列类检测接收 pd.DataFrame。

        Returns:
            list[tuple]: 检测结果列表，每个元素为 (类型, 位置, 描述, 严重程度)。
        """
        ...
