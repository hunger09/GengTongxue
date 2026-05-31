import numpy as np
from collections import Counter
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def _extract_last_digits(values: np.ndarray) -> list[int]:
    last_digits = []
    for v in values:
        s = f"{abs(round(v, 10)):g}"
        for ch in reversed(s):
            if ch.isdigit():
                last_digits.append(int(ch))
                break
    return last_digits


def render_charts(parent_frame, all_values: np.ndarray):
    """在给定的 tkinter frame 中渲染末位数字分布图和数据值分布直方图。"""
    for widget in parent_frame.winfo_children():
        widget.destroy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 末位数字分布图
    last_digits = _extract_last_digits(all_values)
    if last_digits:
        digit_counts = Counter(last_digits)
        digits = list(range(10))
        counts = [digit_counts.get(d, 0) for d in digits]

        ax1.bar(digits, counts)
        ax1.set_title("末位数字分布")
        ax1.set_xlabel("数字")
        ax1.set_ylabel("出现次数")
        ax1.set_xticks(digits)

        expected = len(last_digits) / 10
        ax1.axhline(y=expected, color='r', linestyle='--', label=f'期望频率({expected:.1f})')
        ax1.legend()

    # 数据值分布直方图
    ax2.hist(all_values, bins=20)
    ax2.set_title("数据值分布直方图")
    ax2.set_xlabel("数值")
    ax2.set_ylabel("频率")

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
