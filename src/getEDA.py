from pathlib import Path
import openai
import os
from LLMTasks import LLMTasks
from loader import load_cached_texts

P = "secrets/.OPENAI_API_KEY"
with open(P, "r") as f:
    openai.api_key = f.read().strip()

def getEDA(text: str, log_path: str, filename: str):
    tasks = LLMTasks("./src/prompts/judge-EDA.txt") | LLMTasks("./src/prompts/translate.txt")
    translated  = tasks.execute(text)
    with open(log_path, "a", encoding="utf-8") as logf:
        logf.write(f"==== {filename} ====\n")
        logf.write(translated + "\n\n")
    print(translated)


# キャッシュされたテキストを読み込む
files = ["test"] # "noEDA","littleEDA",
target_dir = "result2/"
os.makedirs(target_dir,exist_ok=True)

for fl in files:
    cache_dir = f"PDF/cache/{fl}"  # ここを実際のディレクトリに置き換えて
    texts, paths = load_cached_texts(cache_dir)
    
    # 各テキストに対して EDA 推定を実行
    for i in range(5):
        log_file_path = f"{target_dir}{fl}{i+1}.txt"
        max_files = min(99,len(paths))
        readed = 0
        for text, path in zip(texts, paths):
            filename = os.path.basename(path)
            print(f"===={readed+1}/{max_files} {filename} ====")
            getEDA(text, log_file_path, filename)
            print("\n")
            readed += 1
            if readed >= max_files:
                break