import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
import numpy as np

from src.analyzers.digit_dist import DigitDistributionAnalyzer
from src.analyzers.arithmetic import ArithmeticSequenceAnalyzer
from src.analyzers.duplicate import DuplicateDataAnalyzer
from src.analyzers.precision import PrecisionConsistencyAnalyzer
from src.analyzers.stddev import StandardDeviationAnalyzer
from src.analyzers.correlation import HighCorrelationAnalyzer
from src.reporters.chart_gen import render_charts
from src.reporters.html_report import generate_and_open
from src.utils.file_io import load_data, extract_numeric


CHECK_OPTIONS = [
    ("last_digit", "末位数字分布异常"),
    ("arithmetic_seq", "完美等差数列检测"),
    ("duplicate_data", "完全重复数据检测"),
    ("precision", "数据精度一致性检测"),
    ("std_dev", "标准差异常检测"),
    ("correlation", "强相关性检测"),
]


class AcademicDataChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("实验数据自检工具")
        self.root.geometry("900x700")

        self.file_path = None
        self.df = None
        self.suspicious_points = []
        self.column_vars = {}

        self._build_ui()

    def _build_ui(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件选择
        self.file_frame = ttk.LabelFrame(self.main_frame, text="文件选择", padding="10")
        self.file_frame.pack(fill=tk.X, pady=5)

        self.file_label = ttk.Label(self.file_frame, text="未选择文件")
        self.file_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(self.file_frame, text="浏览", command=self._browse_file).pack(side=tk.RIGHT, padx=5)

        # 列选择
        self.column_frame = ttk.LabelFrame(self.main_frame, text="数据列选择（加载文件后显示）", padding="10")
        self.column_frame.pack(fill=tk.X, pady=5)

        self.column_hint = ttk.Label(self.column_frame, text="请先选择文件")
        self.column_hint.pack(side=tk.LEFT, padx=5)

        # 检测选项
        self.options_frame = ttk.LabelFrame(self.main_frame, text="检测选项", padding="10")
        self.options_frame.pack(fill=tk.X, pady=5)

        self.check_vars = {key: tk.BooleanVar(value=True) for key, _ in CHECK_OPTIONS}

        row, col = 0, 0
        for key, text in CHECK_OPTIONS:
            ttk.Checkbutton(self.options_frame, text=text, variable=self.check_vars[key]).grid(
                row=row, column=col, sticky=tk.W, padx=10, pady=2
            )
            col += 1
            if col > 2:
                col = 0
                row += 1

        # 检测按钮
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="开始检测", command=self._run_check).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="生成详细报告", command=self._generate_report).pack(side=tk.LEFT, padx=5)

        # 结果区域
        self.result_frame = ttk.LabelFrame(self.main_frame, text="检测结果", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.notebook = ttk.Notebook(self.result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 可疑点列表
        list_frame = ttk.Frame(self.notebook)
        self.notebook.add(list_frame, text="可疑点列表")

        self.result_tree = ttk.Treeview(list_frame, columns=("类型", "位置", "描述", "严重程度"), show="headings")
        for col_id, heading, width in [
            ("类型", "异常类型", 120), ("位置", "位置", 100),
            ("描述", "描述", 450), ("严重程度", "严重程度", 80),
        ]:
            self.result_tree.heading(col_id, text=heading)
            self.result_tree.column(col_id, width=width)
        self.result_tree.pack(fill=tk.BOTH, expand=True)

        # 统计图表
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="统计图表")

        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ── 文件操作 ──

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel文件", "*.xlsx;*.xls;*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                self.df = load_data(file_path)
            except Exception as e:
                messagebox.showerror("错误", f"读取文件时出错: {str(e)}")
                return

            self.file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.status_bar.config(text=f"已选择文件: {file_path}")
            self._update_column_selector(self.df)
            self._clear_results()

    def _clear_results(self):
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.suspicious_points = []

    def _update_column_selector(self, df: pd.DataFrame):
        """加载文件后刷新列选择器，显示所有数值列。"""
        self.column_hint.pack_forget()
        for widget in self.column_frame.winfo_children():
            widget.destroy()

        self.column_vars.clear()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            ttk.Label(self.column_frame, text="文件中未找到数值列").pack(side=tk.LEFT, padx=5)
            return

        # 全选/全不选按钮
        btn_frame = ttk.Frame(self.column_frame)
        btn_frame.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="全选", command=self._select_all_columns).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="全不选", command=self._deselect_all_columns).pack(side=tk.LEFT, padx=2)

        for col_name in numeric_cols:
            var = tk.BooleanVar(value=True)
            self.column_vars[col_name] = var
            ttk.Checkbutton(self.column_frame, text=col_name, variable=var).pack(side=tk.LEFT, padx=5)

    def _select_all_columns(self):
        for var in self.column_vars.values():
            var.set(True)

    def _deselect_all_columns(self):
        for var in self.column_vars.values():
            var.set(False)

    def _get_selected_columns(self) -> list[str]:
        """返回用户勾选的数值列名。"""
        selected = [col for col, var in self.column_vars.items() if var.get()]
        return selected

    # ── 检测流程 ──

    def _run_check(self):
        if not self.file_path:
            messagebox.showwarning("警告", "请先选择一个Excel文件")
            return

        try:
            self.status_bar.config(text="正在读取文件...")
            self.root.update()

            self._clear_results()

            selected_cols = self._get_selected_columns()
            if not selected_cols:
                messagebox.showwarning("警告", "请至少选择一列数据")
                self.status_bar.config(text="请至少选择一列数据")
                return

            numeric_df = self.df[selected_cols]
            all_values = extract_numeric(numeric_df)

            if len(all_values) == 0:
                messagebox.showinfo("信息", "所选列中未找到数值型数据")
                self.status_bar.config(text="检测完成：未找到数值型数据")
                return

            self.status_bar.config(text="正在进行数据分析...")
            self.root.update()

            analyzers = self._get_enabled_analyzers()
            for analyzer, key, needs_df in analyzers:
                data = numeric_df if needs_df else all_values
                self.suspicious_points.extend(analyzer.analyze(data))

            for point in self.suspicious_points:
                self.result_tree.insert("", tk.END, values=point)

            if self.suspicious_points:
                self.status_bar.config(text=f"检测完成：共发现 {len(self.suspicious_points)} 个可疑点")
            else:
                self.status_bar.config(text="检测完成：暂未发现可疑情况")
            render_charts(self.chart_frame, all_values)

        except Exception as e:
            messagebox.showerror("错误", f"处理文件时出错: {str(e)}")
            self.status_bar.config(text="检测失败")

    def _get_enabled_analyzers(self):
        """返回 (analyzer_instance, check_var_key, needs_dataframe) 列表。"""
        mapping = [
            (DigitDistributionAnalyzer(), "last_digit", False),
            (ArithmeticSequenceAnalyzer(), "arithmetic_seq", True),
            (DuplicateDataAnalyzer(), "duplicate_data", False),
            (PrecisionConsistencyAnalyzer(), "precision", False),
            (StandardDeviationAnalyzer(), "std_dev", True),
            (HighCorrelationAnalyzer(), "correlation", True),
        ]
        return [(a, k, df) for a, k, df in mapping if self.check_vars[k].get()]

    # ── 报告 ──

    def _generate_report(self):
        if not self.suspicious_points:
            messagebox.showinfo("信息", "没有可疑点需要报告")
            return

        report_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML文件", "*.html"), ("所有文件", "*.*")],
            initialfile="学术数据检测报告.html"
        )
        if not report_path:
            return

        try:
            generate_and_open(report_path, self.file_path, self.suspicious_points)
            messagebox.showinfo("成功", f"报告已生成: {report_path}")
        except Exception as e:
            messagebox.showerror("错误", f"生成报告时出错: {str(e)}")
