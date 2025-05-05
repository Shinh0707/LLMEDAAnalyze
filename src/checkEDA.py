#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path
import openai
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from LLM.LLMTasks import LLMTasks
from preprocess.loader import load_api_key, load_cached_texts
from export.result import ReportFormat, report_result
from processors.over_folders import read_folder_and_report

EXE_DATETIME   = datetime.now()
TESTED_FOLDER  = ["unstables"]  # 他に "noEDA","littleEDA" など
MODEL_NAME     = "o4-mini-2025-04-16"
RESULT_DIR     = "result/judgeEDA"
REPEAT_TIME    = 5
MAX_WORKERS    = 3         # 並行実行数
REPORT_FORMAT  = ReportFormat.JSONS

def judgeEDA():    return LLMTasks("./src/prompts/judge-EDA.txt")
TASKS = judgeEDA()

def run_trial(texts, paths, model_name, tasks, output_path: Path):
    """
    1 trial分の LLM 実行とレポート出力を行う。
    """
    outputs = read_folder_and_report(texts, paths, tasks, model_name)
    report_result(outputs, output_path)

def main():
    openai.api_key = load_api_key()

    # 結果フォルダ作成
    result_folder = Path(RESULT_DIR) / EXE_DATETIME.strftime("%Y%m%d_%H%M%S")
    result_folder.mkdir(parents=True, exist_ok=True)

    # 各フォルダごとに処理
    for fl in TESTED_FOLDER:
        cache_dir = f"PDF/cache/{fl}"
        texts, paths = load_cached_texts(cache_dir)

        # 並列実行用スレッドプールを作成
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            # REPEAT_TIME 回分のジョブを submit
            for i in range(REPEAT_TIME):
                trial_name   = f"{fl}{i}"
                output_path  = result_folder / f"{trial_name}.json"
                futures.append(
                    executor.submit(
                        run_trial,
                        texts, paths,
                        MODEL_NAME, TASKS,
                        output_path
                    )
                )

            # 完了を tqdm で待つ
            for _ in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {fl}"):
                pass

if __name__ == "__main__":
    main()
