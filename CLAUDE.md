# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

实验数据自检工具 (Experiment Data Self-Check Tool) — Windows 桌面应用，用于自动分析 Excel/CSV 文件中的数据，检测统计学异常并生成可疑点报告。

## Development Environment

- **Python**: 3.10 (venv: `.geng`)
- **激活环境**: `.geng\Scripts\activate`
- **运行**: `python main.py`
- **安装依赖**: `pip install -r requirements.txt`

## Directory Structure

```
selfexam/
├── main.py                 # 程序入口
├── src/
│   ├── __init__.py
│   ├── ui/                 # GUI 界面层
│   │   ├── __init__.py
│   │   ├── main_window.py  # 主窗口 (AcademicDataChecker)
│   │   └── widgets.py      # 自定义控件
│   ├── analyzers/          # 检测算法层
│   │   ├── __init__.py
│   │   ├── base.py         # 检测器基类
│   │   ├── digit_dist.py   # 末位数字分布检测
│   │   ├── arithmetic.py   # 完美等差数列检测
│   │   ├── duplicate.py    # 重复数据检测
│   │   ├── precision.py    # 数据精度一致性检测
│   │   ├── stddev.py       # 标准差异常检测
│   │   └── correlation.py  # 强相关性检测
│   ├── reporters/          # 报告生成层
│   │   ├── __init__.py
│   │   ├── html_report.py  # HTML 报告生成
│   │   └── chart_gen.py    # Matplotlib 图表生成
│   └── utils/              # 工具函数
│       ├── __init__.py
│       └── file_io.py      # 文件读取 (Excel/CSV)
├── resources/              # 静态资源 (图标、模板等)
├── tests/                  # 测试
│   └── ...
├── requirements.txt
├── README.md
└── CLAUDE.md
```

## Architecture

三层架构: **UI 层** → **检测算法层** → **报告生成层**

- **UI 层** (`src/ui/`): tkinter 界面，文件选择、检测选项、结果展示 (Treeview)、图表嵌入 (FigureCanvasTkAgg)
- **检测算法层** (`src/analyzers/`): 每个检测项独立一个模块，基于 pandas DataFrame 和 numpy 数组操作，检测结果统一为 `(类型, 位置, 描述, 严重程度)` 四元组
- **报告生成层** (`src/reporters/`): HTML 报告 + matplotlib 图表，报告使用 severity 分级着色 (high/medium/low)

## Key Conventions

- 检测算法输入统一: 数值类检测接收 `np.ndarray`，列类检测接收 `pd.DataFrame`
- 浮点比较容差: `1e-10`
- matplotlib 中文字体: `SimHei`
- 所有 UI 文本使用中文
- 异常严重程度用 emoji 星级表示: ⭐⭐⭐⭐⭐ / ⭐⭐⭐⭐ / ⭐⭐⭐

## Packaging

使用 PyInstaller 打包为 Windows exe:
```
pip install pyinstaller
pyinstaller --onefile --windowed --name "学术数据检测工具" main.py
```
