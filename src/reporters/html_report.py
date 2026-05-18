import os
import webbrowser
import pandas as pd


HTML_TEMPLATE_HEAD = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>学术数据检测报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .high {{ background-color: #ffcccc; }}
        .medium {{ background-color: #ffffcc; }}
        .low {{ background-color: #ccffcc; }}
        .summary {{ margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>学术数据造假检测报告</h1>
    <div class="summary">
        <p><strong>检测文件:</strong> {file_name}</p>
        <p><strong>检测时间:</strong> {time}</p>
        <p><strong>发现可疑点总数:</strong> {count}</p>
    </div>
    <h2>可疑点详情</h2>
    <table>
        <tr>
            <th>序号</th>
            <th>异常类型</th>
            <th>位置</th>
            <th>描述</th>
            <th>严重程度</th>
        </tr>
"""

HTML_TEMPLATE_ROW = """\
        <tr class="{severity_class}">
            <td>{index}</td>
            <td>{type}</td>
            <td>{location}</td>
            <td>{description}</td>
            <td>{severity}</td>
        </tr>
"""

HTML_TEMPLATE_TAIL = """\
    </table>
    <h2>重要说明</h2>
    <ul>
        <li>本报告仅基于统计学规律检测数据异常，不能直接判定为学术造假</li>
        <li>统计学异常可能由多种原因引起，包括实验设计、数据采集方式等</li>
        <li>最终是否构成学术不端需要学术机构进行全面调查</li>
        <li>建议对标记为高风险的可疑点进行重点核查</li>
    </ul>
</body>
</html>
"""


def _severity_class(severity: str) -> str:
    if "⭐⭐⭐⭐⭐" in severity:
        return "high"
    if "⭐⭐⭐⭐" in severity:
        return "medium"
    return "low"


def generate_and_open(report_path: str, file_path: str, suspicious_points: list[tuple]):
    """生成 HTML 报告并在浏览器中打开。"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE_HEAD.format(
            file_name=os.path.basename(file_path),
            time=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            count=len(suspicious_points)
        ))

        for i, point in enumerate(suspicious_points, 1):
            f.write(HTML_TEMPLATE_ROW.format(
                severity_class=_severity_class(point[3]),
                index=i,
                type=point[0],
                location=point[1],
                description=point[2],
                severity=point[3],
            ))

        f.write(HTML_TEMPLATE_TAIL)

    webbrowser.open(report_path)
