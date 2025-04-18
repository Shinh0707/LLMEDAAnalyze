from datetime import date, datetime
from pathlib import Path
import openai
import os
from LLMTasks import LLMTasks
from loader import load_cached_texts
from utility import extract_last_code_block


EXE_DATETIME = datetime.now()
TESTED_FOLDER = ["test"] # "noEDA","littleEDA",
MODEL_NAME = "o4-mini-2025-04-16"
RESULT_DIR = "result/o4-mini"
REPEAT_TIME = 1

def judgeEDA():     return LLMTasks("./src/prompts/judge-EDA.txt") | LLMTasks("./src/prompts/translate.txt")
def extractEDA():   return LLMTasks("./src/prompts/extract-EDA.txt")
TASKS = judgeEDA()

def main():
    # openaiのキーを設定しておく
    P = "secrets/.OPENAI_API_KEY"
    with open(P, "r") as f:
        openai.api_key = f.read().strip()
    # 実験する
    result_folder = Path(RESULT_DIR)/EXE_DATETIME.strftime("%Y%m%d_%H%M%S")
    os.makedirs(result_folder,exist_ok=True)
    for fl in TESTED_FOLDER:
        cache_dir = f"PDF/cache/{fl}"
        texts, paths = load_cached_texts(cache_dir)
        # 各テキストに対して EDA 推定を実行
        for i in range(REPEAT_TIME):
            log_file_path = result_folder/f"{fl}{i}.json"
            read_folder_and_report(texts, paths, f"{log_file_path}")

def read_folder_and_report(
        papers:list[str],
        paths:list[str],
        result_file_path:str,
        max_limit_files:int = 99
    ):
    """
    paths[i]に格納されている論文papers[i]を読み、求めたタスクに対する結果を
    """
    readed_count = 0
    max_files = min(max_limit_files,len(paths))
    for text, path in zip(papers, paths):
        print(f"===={readed_count+1}/{max_files} {os.path.basename(path)} ====")
        translated = judgeEDA().execute(text, MODEL_NAME)
        report_result(translated, result_file_path)
        readed_count += 1
        if readed_count >= max_files: break

def report_result(
        answer_from_LLM: str, json_file_path: str,
    ):    
    json_data = extract_last_code_block(answer_from_LLM)
    # ログ出力
    with open(json_file_path, "a", encoding="utf-8") as logf:
        logf.write(json_data)
    # 標準出力
    print(json_data)
    print("\n")


if __name__ == "__main__":
    main()