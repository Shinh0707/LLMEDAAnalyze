import os
import json
import csv
import math
from collections import Counter
import fugashi

# --- 二値エントロピーを計算する関数 ---
def binary_entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

# --- 意味あるチャンク抽出（前出） ---
EXCLUDE_SURFACE = {"さ","し","する","いる","よう","なる","ある","てる",
                   "した","して","された","られる","できる","こと","もの","いく"}
def extract_meaningful_chunks(text):
    tagger = fugashi.Tagger()
    tokens = list(tagger(text))
    results, buffer, prev_pos1 = [], "", ""
    for word in tokens:
        surf = word.surface
        lemma = word.feature.lemma
        pos1 = word.feature.pos1
        if pos1 in {"助詞","助動詞","記号"} or lemma in EXCLUDE_SURFACE or surf in EXCLUDE_SURFACE:
            buffer = ""; prev_pos1 = ""; continue
        if pos1 == "接頭辞":
            buffer = surf; prev_pos1 = pos1; continue
        if pos1 == "接尾辞" and results:
            results[-1] += surf; buffer = ""; prev_pos1 = ""; continue
        if prev_pos1 == "副詞" and pos1 in {"名詞","動詞","形容詞"}:
            results[-1] += surf; buffer = ""; prev_pos1 = ""; continue
        if prev_pos1 == "接頭辞":
            results.append(buffer + surf); buffer = ""
        elif pos1 in {"名詞","動詞","形容詞","副詞"}:
            results.append(surf)
        prev_pos1 = pos1
    return set(results)

def get_top_meanful_tokens(reason_texts, top_n=10):
    counter = Counter()
    for txt in reason_texts:
        counter.update(extract_meaningful_chunks(txt))
    return [tok for tok,_ in counter.most_common(top_n)]


def aggregate_with_entropy_per_req(
    input_dir: str,
    output_csv: str,
    top_n=10
):
    req_keys = ['要件1','要件2','要件3','要件4']
    combo_defs = {'要件1&2&4': ['要件1','要件2','要件4']}
    reason_keys = {k: f"{k}の理由" for k in req_keys}

    # stats[path] = {
    #   'counts': { req: {total, true}, ... },
    #   'combos': { combo_name: {total, true}, ... },
    #   'reasons': { req: [理由テキスト,...], ... }
    # }
    stats = {}
    for fname in os.listdir(input_dir):
        if not fname.endswith('.json'): continue
        full = os.path.join(input_dir, fname)
        with open(full, encoding='utf-8') as f:
            data = json.load(f)

        for path, vals in data.items():
            fname = os.path.basename(path)
            if fname not in stats:
                stats[fname] = {
                    'counts': {k:{'total':0,'true':0} for k in req_keys},
                    'combos': {c:{'total':0,'true':0} for c in combo_defs},
                    'reasons': {k:[] for k in req_keys}
                }
            info = stats[fname]

            # 単一要件
            for k in req_keys:
                if k in vals:
                    info['counts'][k]['total'] += 1
                    if vals[k] is True:
                        info['counts'][k]['true'] += 1
                # 理由の収集（文字列なら）
                rk = reason_keys[k]
                if rk in vals and isinstance(vals[rk], str):
                    info['reasons'][k].append(vals[rk])

            # 複合条件
            for combo_name, keys in combo_defs.items():
                info['combos'][combo_name]['total'] += 1
                if all(vals.get(k) is True for k in keys):
                    info['combos'][combo_name]['true'] += 1

    # CSV 出力
    with open(output_csv, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.writer(cf)
        # ヘッダー: 単一要件エントロピー + 複合条件エントロピー + top_tokens_要件X...
        header = (['file_path']
                  + req_keys
                  + list(combo_defs.keys())
                  + [f"top_tokens_{k}" for k in req_keys])
        writer.writerow(header)

        for path, info in stats.items():
            row = [path]
            # (1) 単一要件エントロピー
            for k in req_keys:
                cnt = info['counts'][k]
                p = cnt['true']/cnt['total'] if cnt['total']>0 else 0.0
                row.append(f"{p:.3f}")
            # (2) 複合条件エントロピー
            for combo_name in combo_defs:
                cnt = info['combos'][combo_name]
                p = cnt['true']/cnt['total'] if cnt['total']>0 else 0.0
                row.append(f"{p:.3f}")
            # (3) 要件ごとの上位トークン
            for k in req_keys:
                top_tokens = get_top_meanful_tokens(info['reasons'][k], top_n=top_n)
                row.append(";".join(top_tokens))
            writer.writerow(row)



if __name__ == "__main__":
	aggregate_with_entropy_per_req('result/judgeEDA/renewal', 'output.csv', top_n=5)
