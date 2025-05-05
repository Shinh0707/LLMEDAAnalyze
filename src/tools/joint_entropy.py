#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import math
import argparse

def binary_entropy(p: float) -> float:
    """
    二値エントロピー H(p) = -p log2 p - (1-p) log2 (1-p)
    p=0 または p=1 のときは 0 とみなす
    """
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def compute_joint_entropy(csv_path: str, col_name: str = "要件1&2&4") -> float:
    total_entropy = 0.0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if col_name not in reader.fieldnames:
            raise ValueError(f"列名 '{col_name}' が見つかりません。CSV ヘッダーを確認してください。")
        for row in reader:
            try:
                p = float(row[col_name])
            except (ValueError, TypeError):
                # 不正な値はスキップ
                continue
            total_entropy += binary_entropy(p)
    return total_entropy

def main():
    parser = argparse.ArgumentParser(
        description="CSV の指定列から各行の二値エントロピーを計算し、その総和（結合エントロピー）を出力する。"
    )
    parser.add_argument("csv_path", help="入力 CSV ファイルへのパス")
    parser.add_argument(
        "--column", "-c",
        default="要件1&2&4",
        help="確率が格納されている列名 (デフォルト: 要件1&2&4)"
    )
    args = parser.parse_args()

    H = compute_joint_entropy(args.csv_path, args.column)
    print(f"結合エントロピー (sum H) = {H:.6f}")

if __name__ == "__main__":
    main()
