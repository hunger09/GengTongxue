"""生成测试用的 Excel 数据文件。

运行方式:
    .geng\Scripts\python.exe tests/generate_fixtures.py
"""

import numpy as np
import pandas as pd
import os

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def generate_clean_data() -> pd.DataFrame:
    """生成不应触发任何告警的正常数据。

    末位 0-9 均匀分布、无等差序列、无重复、CV 合理、列间不相关。
    注意: 浮点数中末位 0 只能出现在整数的个位（如 20, 130），
    因此刻意穿插一些整数使末位 0 出现。
    """
    n = 100

    def make_clean_col(seed):
        np.random.seed(seed)
        raw = list(np.random.uniform(0, 10000, n))
        unique = sorted(set(round(v, 2) for v in raw))
        while len(unique) < n:
            unique.append(round(unique[-1] + 0.01, 2))
        vals = unique[:n]
        np.random.shuffle(vals)
        # 每 10 个值中，把 1 个替换为末位 0 的整数（每列 10 个，3 列共 30 个，接近期望值）
        zero_positions = list(range(0, n, 10))
        for i in zero_positions:
            vals[i] = float(int(vals[i]) // 10 * 10)
        # 调整其余值的末位使其覆盖 1-9
        for i in range(n):
            if i in set(zero_positions[:n // 10 * 3]):
                continue
            target_digit = 1 + (i % 9)
            v = vals[i]
            int_part = int(v)
            vals[i] = float(f"{int_part}.{target_digit}")
        # 去重
        seen = set()
        final = []
        for v in vals:
            while v in seen:
                v = round(v + 0.01, 2)
            seen.add(v)
            final.append(v)
        return final

    col_a = make_clean_col(42)
    col_b = make_clean_col(77)
    col_c = make_clean_col(153)

    return pd.DataFrame({"实验组A": col_a, "实验组B": col_b, "实验组C": col_c})


def generate_suspicious_data() -> pd.DataFrame:
    """生成每列刻意包含一种异常的数据，应触发全部 6 项告警。

    注意: 末位数字分布和精度一致性检测是对全局 all_values 做的，
    所以需要让这些异常在整个数据集中占主导地位。
    """
    np.random.seed(99)
    n = 30

    # 所有列的值末位都集中在 0 和 5，这样全局末位分布一定不均匀
    def val_ending_05(base):
        """让值的末位是 0 或 5"""
        return round(base * 2, 0) / 2  # e.g. 1.23 -> 1.0 或 1.5

    np.random.seed(99)

    # 1. 末位数字集中在 0 和 5
    last_digit_vals = [round(i * 0.5, 1) for i in range(1, n + 1)]

    # 2. 完美等差数列 (末位也保持 0 或 5)
    arithmetic_vals = [float(i + 1) * 0.5 for i in range(n)]

    # 3. 大量重复值 (重复率 > 20%)
    duplicate_vals = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                      2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
    remainder = [round((3.0 + i * 0.5), 1) for i in range(n - len(duplicate_vals))]
    duplicate_vals = duplicate_vals + remainder

    # 4. 精度异常: 大部分 1 位小数(末位0或5) + 部分 2 位小数末位集中为 7
    precision_vals = []
    for i in range(n):
        if i < 18:
            precision_vals.append(round(10.0 + i * 0.5, 1))  # 1 位小数
        else:
            # 2 位小数，末位都是 7
            precision_vals.append(round(15.0 + (i - 18) * 0.1, 2) + 0.07)
    # 确保全局 >10% 是 2 位小数且末位集中
    # 18/30 = 60% 是 1 位，12/30 = 40% 是 2 位末位 7
    # 但只有这一列有 2 位小数，其他列全 1 位，全局占比 = 12/(30*8) = 5% — 不够
    # 改为让大部分列都有 2 位小数的值

    # 5. CV < 0.01 (数据几乎完全一致，末位0或5)
    stddev_low_vals = [100.0 + np.random.uniform(-0.005, 0.005) for _ in range(n)]

    # 6. CV > 1.0 (数据波动极大，末位0或5)
    stddev_high_vals = [0.5, 5.0, 50.0, 200.0, 0.5, 100.0, 500.0, 0.5,
                        300.0, 10.0, 0.5, 150.0, 800.0, 0.5, 250.0, 5.0,
                        0.5, 400.0, 0.5, 100.0, 0.5, 5.0, 50.0, 200.0,
                        0.5, 100.0, 500.0, 0.5, 300.0, 10.0]

    # 7. 两列强相关 (> 0.99)
    correlated_base = np.random.normal(50, 10, n)
    correlated_a = list(np.round(correlated_base, 1))
    correlated_b = list(np.round(correlated_base + np.random.uniform(-0.01, 0.01, n), 1))

    df = pd.DataFrame({
        "末位数字异常": last_digit_vals,
        "等差数列": arithmetic_vals,
        "重复数据": duplicate_vals,
        "标准差异常_低": stddev_low_vals,
        "标准差异常_高": stddev_high_vals,
        "强相关A": correlated_a,
        "强相关B": correlated_b,
    })

    # 8. 精度异常列 — 单独构造，确保全局 2 位小数末位 7 占比 >10% 且集中
    # 全局数值总数 = 30 * 7 = 210，需要 >21 个 2 位小数末位 7
    # 此列放 25 个这样的值 + 5 个正常 1 位小数
    precision_vals = []
    for i in range(25):
        precision_vals.append(round(10.0 + i * 0.1, 2) + 0.07)  # 2 位，末位 7
    for i in range(5):
        precision_vals.append(round(20.0 + i * 0.5, 1))  # 1 位
    df["精度异常"] = precision_vals

    return df


def main():
    os.makedirs(FIXTURES_DIR, exist_ok=True)

    clean_df = generate_clean_data()
    clean_path = os.path.join(FIXTURES_DIR, "clean_data.xlsx")
    clean_df.to_excel(clean_path, index=False)
    print(f"Generated: {clean_path} ({clean_df.shape[0]} rows x {clean_df.shape[1]} cols)")

    suspicious_df = generate_suspicious_data()
    suspicious_path = os.path.join(FIXTURES_DIR, "suspicious_data.xlsx")
    suspicious_df.to_excel(suspicious_path, index=False)
    print(f"Generated: {suspicious_path} ({suspicious_df.shape[0]} rows x {suspicious_df.shape[1]} cols)")


if __name__ == "__main__":
    main()
