#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from tqdm import tqdm
from datetime import datetime
from typing import List, Tuple

import openai

from LLM.LLMTasks import LLMTasks
from aggregation import analyze_json
from preprocess.loader import load_api_key, load_cached_texts
from export.result import ReportFormat, report_result
from processors.over_folders import read_folder_and_report
from tools import joint_entropy

# 定数
MODEL_NAME: str = "o4-mini-2025-04-16"
REPORT_FORMAT: ReportFormat = ReportFormat.JSONS


def parse_args() -> argparse.Namespace:
	"""
	コマンドライン引数を解析し、Namespace オブジェクトを返す
	"""
	parser: argparse.ArgumentParser = argparse.ArgumentParser(
		description="Judge EDA for a specified folder and output results to a directory"
	)
	parser.add_argument(
		'-f', '--folder',
		required=True,
		help='Folder name under PDF/cache to process'
	)
	parser.add_argument(
		'-o', '--result-dir',
		default='result/judgeEDA',
		help='Directory to store result files (no timestamp subfolders)'
	)
	parser.add_argument(
		'-r', '--repeat',
		type=int,
		default=5,
		help='Number of times to repeat each trial'
	)
	parser.add_argument(
		'-w', '--workers',
		type=int,
		default=5,
		help='Number of parallel workers'
	)
	return parser.parse_args()


def judgeEDA_task() -> LLMTasks:
	"""
	LLMTasks を初期化して返す
	"""
	return LLMTasks("./src/prompts/judge-EDA.txt")


def run_trial(
	texts: List[str],
	paths: List[str],
	model_name: str,
	tasks: LLMTasks,
	output_path: Path
) -> None:
	"""
	1回分の LLM 実行とレポート出力を行う
	"""
	outputs = read_folder_and_report(texts, paths, tasks, model_name)
	report_result(outputs, output_path)

def read_papers_in_paralell(
		cache_dir:Path,
		result_folder:Path,
		args:argparse.Namespace,
):
	# LLM タスク準備
	tasks: LLMTasks = judgeEDA_task()
	
	if not cache_dir.exists() or not cache_dir.is_dir():
		raise FileNotFoundError(f"Cache folder not found: {cache_dir}")

	texts, paths = load_cached_texts(str(cache_dir)) 

	# 並列実行
	with ThreadPoolExecutor(max_workers=args.workers) as executor:
		futures:list[Future] = []
		for i in range(args.repeat):
			trial_name: str = f"{args.folder}{i}"
			output_path: Path = result_folder / f"{trial_name}.json"
			futures.append(
				executor.submit(
					run_trial,
					texts,
					paths,
					MODEL_NAME,
					tasks,
					output_path
				)
			)

		for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc=f"Processing {args.folder}"
        ):
			try:
				# 結果を取得することで例外を検出
				future.result()
			except Exception as e:
				print(f"Error in future {future}: {e}")

def main() -> None:
	"""
	エントリーポイント: コマンドライン引数の解析、EDA タスクの実行
	"""
	args: argparse.Namespace = parse_args()
	# APIキー設定
	openai.api_key = load_api_key()

	# 結果ディレクトリ作成
	result_folder: Path = Path(args.result_dir)
	result_folder.mkdir(parents=True, exist_ok=True)

	cache_root: Path = Path('PDF/cache')
	folder: str = args.folder
	cache_dir: Path = cache_root / folder
	read_papers_in_paralell(cache_dir, result_folder, args)
	
	aggregation_path = str(result_folder/"agg.csv")
	analyze_json.aggregate_with_entropy_per_req(str(result_folder), aggregation_path, 10)
	
	for column in ["要件1", "要件2", "要件3", "hasEDA"]:
		p = joint_entropy.compute_joint_entropy(aggregation_path, column)
		print(f"H({column}) = {p}")


if __name__ == '__main__':
	main()
