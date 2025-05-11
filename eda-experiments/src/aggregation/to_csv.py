import json
import csv
import glob
import os

bool_columns = ["Design Targeted EDA", "Propose EDA", "Analyze EDA"]

def to_bool(v):
    return str(v).lower() == "true"


def readeEDAresult(input_path: str):
    data_entries = []

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_filename = None
    current_json_lines = []

    # ファイル内の各ブロックは "==== ファイル名 ====" で区切られ、その後に JSON が続く
    for line in lines:
        line = line.strip()
        # コードフェンスとしての ```json や ``` はスキップ
        if line.startswith("```"):
            continue

        # "====" で始まり "====" で終わる行はブロックの区切り
        if line.startswith("====") and line.endswith("===="):
            if current_json_lines:
                json_str = "\n".join(current_json_lines)
                try:
                    data = json.loads(json_str)
                    data["filename"] = current_filename
                    # リスト形式のデータをセミコロン区切り文字列に変換
                    if "Targets" in data and isinstance(data["Targets"], list):
                        data["Targets"] = ";".join(data["Targets"])
                    if "EDA" in data and isinstance(data["EDA"], list):
                        data["EDA"] = ";".join(data["EDA"])
                    # Include EDA フラグの計算
                    data["Include EDA"] = (
                        to_bool(data.get("Design Targeted EDA", "false"))
                        and (to_bool(data.get("Propose EDA", "false"))
                             or to_bool(data.get("Analyze EDA", "false")))
                    )
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
            if line:
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
            data["Include EDA"] = (
                to_bool(data.get("Design Targeted EDA", "false"))
                and (to_bool(data.get("Propose EDA", "false"))
                     or to_bool(data.get("Analyze EDA", "false")))
            )
            data_entries.append(data)
        except Exception as e:
            print(f"JSONパースエラー (ファイル名: {current_filename}): {e}")

    return data_entries


def readallEDAresult(input_dir: str, output_path: str):
    data_entries = []
    data_files = glob.glob(os.path.join(input_dir, "*.txt"))
    for df in data_files:
        data_entries.extend(readeEDAresult(df))

    # CSVヘッダを全キーの集合から取得
    all_keys = set()
    for entry in data_entries:
        all_keys.update(entry.keys())
    headers = list(all_keys)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for entry in data_entries:
            writer.writerow(entry)

    print("CSVへの変換が完了しました。")


if __name__ == "__main__":
    readallEDAresult("result2", "eda.csv")
