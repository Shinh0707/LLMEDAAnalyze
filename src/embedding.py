import pandas as pd
import glob
import os
from tqdm import tqdm
import openai
import numpy as np


# APIキーを読み込む
P = "secrets/.OPENAI_API_KEY"
with open(P, "r") as f:
    client = openai.OpenAI(api_key=f.read().strip())


# 埋め込み取得関数
def get_embedding(text: str, model: str = "text-embedding-3-large"):
    response = client.embeddings.create(
        input=text,
        model=model,
        encoding_format="float"
    )
    return np.array(response.data[0].embedding)

# テキストファイルのパス一覧を取得
txt_files = glob.glob("result/o4-mini-extractEDA/20250424_045922/hasEDA0/*.json")

# 結果格納用リスト
records = []

# 各テキストファイルについて処理
for path in tqdm(txt_files):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # テキストをEmbedding
    embedding = get_embedding(text)
    
    # 保存するためにリスト化
    record = {
        "filename": os.path.basename(path),
        **{f"dim_{i}": val for i, val in enumerate(embedding)}
    }
    records.append(record)

# Pandas DataFrameに変換
df = pd.DataFrame(records)

# CSVに保存
df.to_csv("hasEDA_embeddings.csv", index=False)

print("埋め込み完了してCSV保存しました。")
