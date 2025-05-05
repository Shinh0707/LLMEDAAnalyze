#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import argparse

import openai
from LLM.LLMTasks import LLMTasks
from preprocess.loader import load_api_key 

def load_all_runs(folder: str, paper_basename: str):
    """
    フォルダ内のすべての .json ファイルを読み込み、
    key の basename が paper_basename と一致するエントリを抽出して返す。
    戻り値: [
      {
        "source": json_filename,
        "values": { "要件1": bool, "要件1の理由": str, … }
      },
      …
    ]
    """
    runs = []
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(folder, fname)
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for key, vals in data.items():
            if os.path.basename(key) == paper_basename:
                runs.append({
                    "source": fname,
                    "values": vals
                })
    return runs

def find_conflicts(runs):
    """
    runs の中から要件1〜4について True/False が食い違うものを抽出。
    戻り値: {
      "要件1": [
         {"source":…, "claim":True/False, "reason":…}, …
      ],
      …
    }
    """
    req_keys = ['要件1','要件2','要件3','要件4']
    conflicts = {}

    for req in req_keys:
        # 各 run が持つ claim の集合を調べる
        claims = []
        vals_set = set()
        for run in runs:
            vals = run['values']
            if req in vals:
                c = bool(vals[req])
                vals_set.add(c)
                claims.append({
                    "source": run["source"],
                    "claim": c,
                    "reason": vals.get(f"{req}の理由", "").strip()
                })
        if len(vals_set) > 1:
            conflicts[req] = claims

    return conflicts

def build_prompt(paper_basename, conflicts):
    """
    summarize-conflict.txt のテンプレートを読み込み、
    conflicts の内容を末尾に付与して返す。
    """
    tmpl_path = os.path.join("src", "prompts", "summarize-conflict.txt")
    with open(tmpl_path, encoding='utf-8') as f:
        template = f.read().rstrip()

    lines = [f"論文ID: {paper_basename}"]
    for req, claims in conflicts.items():
        lines.append(f"\n{req}:")
        for c in claims:
            lines.append(f"  - ソース: {c['source']}")
            lines.append(f"    - 主張: {str(c['claim'])}")
            lines.append(f"    - 理由: {c['reason']}")
    payload = template + "\n\n" + "\n".join(lines)
    return payload

def main():
    openai.api_key = load_api_key()
    parser = argparse.ArgumentParser(
        description="指定論文のEDA要件判定の食い違いを集め、LLMに理由を総括させるスクリプト"
    )
    parser.add_argument("folder", help="JSON回答履歴が入ったフォルダパス")
    parser.add_argument("paper", help="論文ファイル名（basename） e.g. IPSJ-EC2024030.txt")
    args = parser.parse_args()

    runs = load_all_runs(args.folder, args.paper)
    if len(runs) < 2:
        print(f"[ERROR] '{args.paper}' に対するランが {len(runs)} 件しかありません。")
        return

    conflicts = find_conflicts(runs)
    if not conflicts:
        print(f"[INFO] '{args.paper}' には要件1～4の間に食い違いは見られません。")
        return

    prompt_text = build_prompt(args.paper, conflicts)

    # LLM呼び出し
    model_name = "o4-mini-2025-04-16"
    task = LLMTasks("src/prompts/summarize-conflict.txt")
    result = task.execute(prompt_text, model_name)

    print("\n=== LLMによる総括 ===\n")
    print(result)

if __name__ == "__main__":
    main()
