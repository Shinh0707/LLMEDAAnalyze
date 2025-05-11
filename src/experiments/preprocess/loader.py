import os

def load_api_key():
    P = "secrets/.OPENAI_API_KEY"
    with open(P, "r") as f:
        return f.read().strip()

def load_cached_texts(cache_dir: str) -> tuple[list[str],list[str]]:
    """
    load cached paper located in `cache_dir`.
    ## returns
    (text[i], file_path[i])
    text[i]: `i`番目にとれた論文の本文
    file_path[i]: `i`番目にとれた論文のパス
    """
    texts = []
    filepaths = []
    
    for file in os.listdir(cache_dir):
        if file.endswith(".txt"):
            path = os.path.join(cache_dir, file)
            with open(path, "r", encoding="utf-8") as f:
                texts.append(f.read())
            filepaths.append(path)
    
    return texts, filepaths