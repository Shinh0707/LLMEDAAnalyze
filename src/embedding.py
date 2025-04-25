from matplotlib import pyplot as plt
import pandas as pd
import glob
import os
import json
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
        dimensions=2,
        encoding_format="float"
    )
    return np.array(response.data[0].embedding)

def json_to_kv_string(json_obj):
    """JSONを key: value / key: value... 形式に整形"""
    return "/".join(json_obj["defined-by-developer-EDA"]+[";"]+json_obj["suggested-EDA"])

def main():
    txt_files = glob.glob("result/o4-mini-extractEDA/20250424_045922/hasEDA0/*.json")
    records = []

    for path in tqdm(txt_files):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)  # JSONとしてロード
        text = json_to_kv_string(data)
        embedding = get_embedding(text)
        record = {
            "filename": os.path.basename(path),
            **{f"dim_{i}": val for i, val in enumerate(embedding)}
        }
        records.append(record)
    return records

records = main()
df = pd.DataFrame(records)
df.to_csv("hasEDA_embeddings2dfiltered3.csv", index=False)
print("埋め込み完了してCSV保存しました。")

# 可視化（filenameを表示）
embedding_cols = [c for c in df.columns if c.startswith("dim_")]
X = df[embedding_cols].to_numpy()

plt.figure(figsize=(8, 8))
plt.scatter(X[:, 0], X[:, 1], s=10)

for i, row in df.iterrows():
    plt.text(row["dim_0"], row["dim_1"], row["filename"], fontsize=7, alpha=0.7)

plt.title("2D Embedding with filename annotations")
plt.xlabel("dim_0")
plt.ylabel("dim_1")
plt.grid(True)
plt.tight_layout()
plt.show()
plt.savefig()
