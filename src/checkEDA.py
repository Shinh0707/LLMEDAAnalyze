from datetime import date, datetime
from enum import Enum
from pathlib import Path
import openai
import os

from tqdm import tqdm
from LLM.LLMTasks import LLMTasks
from preprocess.loader import load_cached_texts
from export.result import ReportFormat


EXE_DATETIME = datetime.now()
TESTED_FOLDER = ["hasEDA"] # "noEDA","littleEDA",
MODEL_NAME = "o4-mini-2025-04-16"
RESULT_DIR = "result/o4-mini-extractEDA"
REPEAT_TIME = 1
REPORT_FORMAT = ReportFormat.JSONS


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
    for fl in tqdm(TESTED_FOLDER):
        cache_dir = f"PDF/cache/{fl}"
        texts, paths = load_cached_texts(cache_dir)
        # 各テキストに対して EDA 推定を実行
        for i in range(REPEAT_TIME):
            trial_name = f"{fl}{i}"
            result_json_folder = result_folder
            outputs = read_folder_and_report(texts, paths, result_json_folder, TASKS, trial_name)
            report_result(outputs, result_json_folder/f"{trial_name}.json")
        


def read_folder_and_report(
        papers:list[str],
        paths:list[str],
        result_json_folder:Path,
        tasks:LLMTasks,
        trial_name:str,
        max_limit_files:int = 99
    ):
    """
    paths[i]に格納されている論文papers[i]を読み、
    求めたタスクに対する結果をJSONファイルとして出力する。
    """
    outputs:dict[str, str] = {}
    readed_count = 0
    max_files = min(max_limit_files,len(paths))
    for text, path in zip(papers, paths):
        print(f"===={readed_count+1}/{max_files} {os.path.basename(path)} ====")
        translated = tasks.execute(text, MODEL_NAME)
        outputs[path] = translated

        readed_count += 1
        if readed_count >= max_files: break
    return outputs

if __name__ == "__main__":
    main()