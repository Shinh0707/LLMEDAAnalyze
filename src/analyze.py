import pandas as pd
from collections import Counter
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

def count_token_appearance(token_sets):
    """各トークンが何件の行に登場したかをカウント"""
    counter = Counter()
    for token_set in token_sets:
        for token in set(token_set):  # 重複しないようにset化
            counter[token] += 1
    return counter

def extract_common_tokens_over_threshold(token_series, tokenizer, threshold=2):
    """シリーズからトークンを抽出し、指定数以上に現れたものだけ返す"""
    token_sets = token_series.dropna().apply(tokenizer).tolist()
    df_counter = count_token_appearance(token_sets)
    common_tokens = [token for token, freq in df_counter.items() if freq >= threshold]
    return sorted(common_tokens)

def tokenize_targets(entry):
    return entry.split(";") if isinstance(entry, str) else []

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
    
    if "Targets" in group.columns:
        common_targets = extract_common_tokens_over_threshold(group["Targets"], tokenize_targets, threshold=2)
        result["共通Targets語（≥2件）"] = ";".join(common_targets)
    
    return pd.Series(result)

aggregated_results = grouped.apply(aggregate_fluctuations)
print(aggregated_results)

# 集計結果を CSV に出力（必要に応じてファイルパスを変更）
aggregated_results.to_csv("eda_aggregated.csv", encoding="utf-8-sig")
