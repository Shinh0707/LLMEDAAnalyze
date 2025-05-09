
import os
from LLM.LLMTasks import LLMTasks
from utility import extract_last_code_block


def read_folder_and_report(
		papers:list[str],
		paths:list[str],
		tasks:LLMTasks,
		model_name:str,
		max_limit_files:int = 999
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
		translated = tasks.execute(text, model_name)
		outputs[path] = extract_last_code_block(translated)
		print(translated)
		readed_count += 1
		if readed_count >= max_files: break
	return outputs
