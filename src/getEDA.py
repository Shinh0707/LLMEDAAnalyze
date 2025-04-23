from datetime import date, datetime
from enum import Enum
from pathlib import Path
import openai
import os
from LLMTasks import LLMTasks
from loader import load_cached_texts
from utility import extract_last_code_block


EXE_DATETIME = datetime.now()
TESTED_FOLDER = ["hasEDA"] # "noEDA","littleEDA",
MODEL_NAME = "o4-mini-2025-04-16"
RESULT_DIR = "result/o4-mini-extractEDA"
REPEAT_TIME = 1

class ReportFormat(Enum):
    LOG = 1
    JSONS = 2
REPORT_FORMAT = ReportFormat.LOG


def judgeEDA():     return LLMTasks("./src/prompts/judge-EDA.txt") | LLMTasks("./src/prompts/translate.txt")
def extractEDA():   return LLMTasks("./src/prompts/extract-EDA.txt")
TASKS = extractEDA()

def main():
    # openaiのキーを設定しておく
    P = "secrets/.OPENAI_API_KEY"
    with open(P, "r") as f:
        openai.api_key = f.read().strip()
    # 実験する
    result_folder = Path(RESULT_DIR)/(EXE_DATETIME.strftime("%Y%m%d_%H%M%S"))
    for fl in TESTED_FOLDER:
        cache_dir = f"PDF/cache/{fl}"
        texts, paths = load_cached_texts(cache_dir)
        # 各テキストに対して EDA 推定を実行
        for i in range(REPEAT_TIME):
            trial_name = f"{fl}{i}"
            result_json_folder = result_folder
            read_folder_and_report(texts, paths, result_json_folder, trial_name)

def read_folder_and_report(
        papers:list[str],
        paths:list[str],
        result_json_folder:Path,
        trial_name:str,
        max_limit_files:int = 99
    ):
    """
    paths[i]に格納されている論文papers[i]を読み、
    求めたタスクに対する結果をJSONファイルとして出力する。
    """
    readed_count = 0
    max_files = min(max_limit_files,len(paths))
    for text, path in zip(papers, paths):
        print(f"===={readed_count+1}/{max_files} {os.path.basename(path)} ====")
        translated = TASKS.execute(text, MODEL_NAME)
        
        if REPORT_FORMAT == ReportFormat.LOG:
            report_result_in_log(translated, result_json_folder/f"{trial_name}.txt", Path(path).name)
        elif REPORT_FORMAT == ReportFormat.JSONS:
            report_result_in_jsons(translated, result_json_folder/trial_name/f"{Path(path).name}.json")
        
        readed_count += 1
        if readed_count >= max_files: break

def report_result_in_log(
        answer_from_LLM: str, log_file_path: Path,
        filename:str
    ):    
    # ログ出力
    os.makedirs(log_file_path.parent,exist_ok=True)
    with open(log_file_path, "a", encoding="utf-8") as logf:
        logf.write(f"==== {filename} ====\n")
        logf.write(answer_from_LLM + "\n\n")
    # 標準出力
    print(answer_from_LLM)
    print("\n")

# FIXME: 一つのファイルに全ての論文のEDAの結果を収めたい
def report_result_in_jsons(
        answer_from_LLM: str, json_file_path: Path,
    ):
    os.makedirs(json_file_path.parent,exist_ok=True)
    json_data = extract_last_code_block(answer_from_LLM)
    # ログ出力
    with open(json_file_path, "a", encoding="utf-8") as logf:
        logf.write(json_data)
    # 標準出力
    print(json_data)
    print("\n")


if __name__ == "__main__":
    main()