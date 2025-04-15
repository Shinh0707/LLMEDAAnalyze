import json
import csv

# 入力と出力ファイルのパス
input_path = "result/hasEDA1.txt"
output_csv = "result/hasEDA1.csv"

data_entries = []

with open(input_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

current_filename = None
current_json_lines = []

# ファイル内の各ブロックは "==== ファイル名 ====" で区切られており、その後に JSON が続く
for line in lines:
    line = line.strip()
    # "====" で始まり "====" で終わる行はブロックの区切り（ファイル名が示されている部分）
    if line.startswith("====") and line.endswith("===="):
        # 前のブロックに JSON 行があればパースしてリストに追加
        if current_json_lines:
            json_str = "\n".join(current_json_lines)
            try:
                data = json.loads(json_str)
                # ブロックのファイル名も保存（キー "filename" として追加）
                data["filename"] = current_filename
                # リスト形式のデータは、CSV上で扱いやすいようにセミコロン区切りの文字列に変換
                if "Targets" in data and isinstance(data["Targets"], list):
                    data["Targets"] = ";".join(data["Targets"])
                if "EDA" in data and isinstance(data["EDA"], list):
                    data["EDA"] = ";".join(data["EDA"])
                data_entries.append(data)
            except Exception as e:
                print(f"JSONパースエラー (ファイル名: {current_filename}): {e}")
            current_json_lines = []
        # 区切り行からファイル名を抽出
        parts = line.split("====")
        if len(parts) >= 2:
            current_filename = parts[1].strip()
    else:
        # 空行でなければ JSON の一部として保持
        if line != "":
            current_json_lines.append(line)

# 最後のブロックが残っている場合の処理
if current_json_lines:
    json_str = "\n".join(current_json_lines)
    try:
        data = json.loads(json_str)
        data["filename"] = current_filename
        if "Targets" in data and isinstance(data["Targets"], list):
            data["Targets"] = ";".join(data["Targets"])
        if "EDA" in data and isinstance(data["EDA"], list):
            data["EDA"] = ";".join(data["EDA"])
        data_entries.append(data)
    except Exception as e:
        print(f"JSONパースエラー (ファイル名: {current_filename}): {e}")

# CSVファイルに書き出すため、全ブロックのキーの集合をヘッダとして取得
all_keys = set()
for entry in data_entries:
    for key in entry.keys():
        all_keys.add(key)
headers = list(all_keys)

with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    for entry in data_entries:
        writer.writerow(entry)

print("CSVへの変換が完了しました。")
