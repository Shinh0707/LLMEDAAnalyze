import os
from pathlib import Path
from openai import OpenAI

openai = OpenAI()

P = "secrets/.OPENAI_API_KEY"
with open(P, "r") as f:
    openai.api_key = f.read().strip()

response = openai.embeddings.create(
    input="Your text string goes here",
    model="text-embedding-3-small"
)

print(response.data[0].embedding)




def report_result_in_log(
    answer_from_LLM: list[float], log_file_path: Path,
    filename:str
    ):
    # ログ出力
    os.makedirs(log_file_path.parent,exist_ok=True)
    with open(log_file_path, "a", encoding="utf-8") as logf:
        logf.write(f"==== {filename} ====\n")
        logf.write(str(answer_from_LLM) + "\n\n")
    # 標準出力
    print(answer_from_LLM)
    print("\n")
