from enum import Enum
import json
import os
from pathlib import Path

from utility import extract_last_code_block


class ReportFormat(Enum):
	LOG = 1
	JSONS = 2

def report_result(
	answers_from_LLM: dict[str, str],
	log_file_path: Path,
):
	if log_file_path.name.endswith(".json"):
		return report_result_in_json(answers_from_LLM, log_file_path)
	else:
		return report_result_in_log(answers_from_LLM, log_file_path)

def report_result_in_log(
		answers_from_LLM: dict[str, str],
		log_file_path: Path,
	):	
	# ログ出力
	os.makedirs(log_file_path.parent,exist_ok=True)
	with open(log_file_path, "w", encoding="utf-8") as logf:
		for filename, answer in answers_from_LLM:
			logf.write(f"==== {filename} ====\n")
			logf.write(answer + "\n\n")

def report_result_in_json(
		answers_from_LLM: dict[str, str],
		log_file_path: Path,
	):
	# ログ出力
	os.makedirs(log_file_path.parent,exist_ok=True)
	structured_answer = {}
	for key, value in answers_from_LLM:
		structured_answer[key] = json.loads(value)
	with open(log_file_path, "w") as f:
		json.dump(answers_from_LLM, f, indent=4)