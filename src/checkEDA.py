from datetime import datetime
from pathlib import Path
import openai
import os

from tqdm import tqdm
from LLM.LLMTasks import LLMTasks
from preprocess.loader import load_api_key, load_cached_texts
from export.result import ReportFormat, report_result
from processors.over_folders import read_folder_and_report


EXE_DATETIME = datetime.now()
TESTED_FOLDER = ["test"] # "noEDA","littleEDA",
MODEL_NAME = "o4-mini-2025-04-16"
RESULT_DIR = "result/end2end-EDA"
REPEAT_TIME = 1
REPORT_FORMAT = ReportFormat.JSONS


def judgeEDA():	 return LLMTasks("./src/prompts/judge-EDA.txt") | LLMTasks("./src/prompts/translate.txt")
def extractEDA():   return LLMTasks("./src/prompts/extract-EDA.txt")
def end2end_extractEDA():   return LLMTasks("./src/prompts/end2end-extractEDA.txt")
TASKS = end2end_extractEDA()

def main():
	openai.api_key = load_api_key()
	# 実験する
	result_folder = Path(RESULT_DIR)/(EXE_DATETIME.strftime("%Y%m%d_%H%M%S"))
	for fl in tqdm(TESTED_FOLDER):
		cache_dir = f"PDF/cache/{fl}"
		texts, paths = load_cached_texts(cache_dir)
		# 各テキストに対して EDA 推定を実行
		for i in range(REPEAT_TIME):
			trial_name = f"{fl}{i}"
			result_json_folder = result_folder
			outputs = read_folder_and_report(texts, paths, TASKS, MODEL_NAME)
			report_result(outputs, result_json_folder/f"{trial_name}.json")


if __name__ == "__main__":
	main()