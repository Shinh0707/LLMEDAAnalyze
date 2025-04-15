import pandas as pd
from ward_analyze import extract_common_meaningful_tokens

# CSVファイルの読み込み（ファイル名は適宜変更）
df = pd.read_csv("eda.csv")

# 必要に応じて、Booleanの値が文字列 ("True"/"False") になっている場合は変換する
bool_columns = ["Design Targeted EDA", "Propose EDA", "Analyze EDA"]
for col in bool_columns:
    # 小文字にして比較するなど、状況に応じた変換を実施
    df[col] = df[col].apply(lambda x: True if str(x).lower() == "true" else False)

# filename 列でグループ化
grouped = df.groupby("filename")

# 各グループごとに出力結果の揺らぎ（ばらつき）の集計を実施
def aggregate_fluctuations(group):
    result = {}
    result["件数"] = len(group)
    
    # 数値データ（Clarity Score）の集計
    if "Clarity Score" in group.columns:
        result["Clarity Score_平均"] = group["Clarity Score"].mean()
        result["Clarity Score_標準偏差"] = group["Clarity Score"].std()
        result["Clarity Score_最小"] = group["Clarity Score"].min()
        result["Clarity Score_最大"] = group["Clarity Score"].max()
    
    # Boolean データの True 比率を算出
    for col in bool_columns:
        true_ratio = group[col].mean()  # True が 1、False が 0 として平均を取る
        result[f"{col}_True比率"] = true_ratio
        result[f"{col}_True件数"] = group[col].sum()
    includeEDA = (group["Design Targeted EDA"] & group["Propose EDA"])
    result["Include EDA_True比率"] = includeEDA.mean()
    result["Include EDA_True件数"] = includeEDA.sum()
    
    # EDA列の共通ワード抽出
    if "EDA" in group.columns:
        common_tokens = extract_common_meaningful_tokens(group["EDA"])
        result["共通EDA形態素"] = ";".join(common_tokens)
    else:
        result["共通EDA形態素"] = ""
    
    return pd.Series(result)

aggregated_results = grouped.apply(aggregate_fluctuations)
print(aggregated_results)

# 集計結果を CSV に出力（必要に応じてファイルパスを変更）
aggregated_results.to_csv("eda_aggregated.csv", encoding="utf-8-sig")
