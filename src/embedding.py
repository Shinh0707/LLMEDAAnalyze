from matplotlib import pyplot as plt
import pandas as pd
import glob
import os
from tqdm import tqdm
import openai
import numpy as np
import umap


# APIキーを読み込む
P = "secrets/.OPENAI_API_KEY"
with open(P, "r") as f:
    client = openai.OpenAI(api_key=f.read().strip())


# 埋め込み取得関数
def get_embedding(text: str, model: str = "text-embedding-3-large"):
    response = client.embeddings.create(
        input=text,
        model=model,
        dimensions=32,
        encoding_format="float"
    )
    return np.array(response.data[0].embedding)
def main():
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
df = pd.read_csv("hasEDA_embeddings.csv")

# "dim_" で始まる列名だけを抽出して行列化
embedding_cols = [c for c in df.columns if c.startswith("dim_")]
X = df[embedding_cols].to_numpy()    # shape = (N_documents, embedding_dim)

# CSVに保存
df.to_csv("hasEDA_embeddings.csv", index=False)

print("埋め込み完了してCSV保存しました。")


# Run UMAP to 2D
reducer = umap.UMAP(
    n_components=2,
    n_neighbors=15,
    min_dist=0.1,
    metric='euclidean',
    random_state=42
)
embedding = reducer.fit_transform(X)

# Scatter plot
plt.figure(figsize=(6, 6))
plt.scatter(embedding[:, 0], embedding[:, 1], s=10)
plt.title("UMAP projection to 2D")
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.tight_layout()
plt.show()
