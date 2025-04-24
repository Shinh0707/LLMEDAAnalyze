import re

def extract_last_code_block(text: str) -> str:
    """
    text 中の ```…``` で囲まれたコードブロック内部をすべて抽出して、そのうち最後のものをリストで返す。
    """
    # オプションで言語指定があっても OK、改行をまたいでマッチする
    pattern = re.compile(r'```json(?:[^\n]*)\n([\s\S]*?)```', re.DOTALL)
    code_blocks = pattern.findall(text)
    assert len(code_blocks) != 0
    return code_blocks[-1]