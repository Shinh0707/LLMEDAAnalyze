import openai
import os

P = "secrets/.OPENAI_API_KEY"
with open(P, "r") as f:
    openai.api_key = f.read().strip()

def getEDA(text: str, log_path: str, filename: str):
    instruction = '''
# Prior Knowledge
    Entertainment Design Assets (EDA) in content refer to expressions that describe the "feeling responses" intended to be evoked in players, as defined in the content's design requirements.
    However, EDA here specifically refers to "mechanisms that directly cause changes in the user's own feeling state."

## Concrete Examples of EDA Items
    “Link to the real world,” “Narrative experiences,”  
    “Performative presentation,” “Elements that make people want to share,”  
    “Intuitive interface,” “Cost-effectiveness dilemma,”  
    “Space for self-expression,” “Collaborative achievement,”  
    “Gradual learning,” “Sense of liberation,” “Shame,” “Guilt,” “Narrative,”  
    “Tactile feedback → Sense of accomplishment,” “Subtlety from rolling a ball,”  
    “Desire to possess web pages or websites,”  
    “Synchronization of motion and audiovisuals”

# Question
    Does the content introduced in this paper contain EDAs?
    To determine the presence of EDAs, please assess whether the following "EDA Conditions" are satisfied within the paper's main theme.

    “EDA Conditions”:
    - "The feeling responses targeted in the user are clearly defined as part of the design requirements of the content."
        - It is important that they are specifically and unambiguously defined by the developers.
        - If the feeling experience varies based on user behavior (i.e., the EDA becomes optional), this condition is not satisfied.
    - "The content aims to deliberately influence the user's own feeling state."
    - "The paper discusses what kind of feeling response the content is expected to evoke when used."

# Response Format
    Please answer in the form of a JSON block like the following:
    ```
    {
        "Targets": string[], // Targets that changes feeling. (No EDA unless “content user” is included here.)
        "Design Targeted EDA Reason": string, // Reason for Design Targeted EDA
        "Design Targeted EDA": boolean, // Whether the feeling response is clearly specified in the content design requirements
        "Propose EDA Reason": string, // Reason for Propose EDA
        "Propose EDA": boolean, // Whether the content aims to influence the user's feeling state
        "Analyze EDA Reason": string, // Reason for Analyze EDA
        "Analyze EDA": boolean, // Whether the paper discusses the feeling response evoked by using the content
        "Clarity Score reason": string, // Reason for the Clarity Score
        "Clarity Score": int, // 4: EDA is a clear main topic, 3: EDA is a main topic but unclear, 2: Not a main topic, 1: No EDA at all
        "EDA": string[], // Direct quotes from the paper describing the targeted feeling responses. Please extract them verbatim in the original language of the paper (do not translate). Leave empty if none.
    }
    ```
    '''
    
    response = openai.chat.completions.create(
        model="o4-mini-2025-04-16",
        messages=[
            {"role": "developer", "content": instruction},
            {"role": "user", "content": text}
        ]
    )
    # モデルからの応答を出力
    # print(response.choices[0].message.content)

    res = response.choices[0].message.content
    if not res:
        return
    
    response_ja = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "developer",
                "content": """
                次のJSONを読み取り、以下のルールに従って翻訳してください：
                - Keyはすべてそのままにしてください（変更禁止）。
                - 最後のKey("EDA")の配列内の値は翻訳しないでください。元の言語のまま保持してください。
                - それ以外の全ての値（文字列,数値）は、日本語に翻訳してください。
                - JSONの構造を壊さずに、JSON形式で返答してください。
                """
            },
            {"role": "user", "content": res}
        ]
    )

    translated = response_ja.choices[0].message.content

    # ログファイルに書き込み
    with open(log_path, "a", encoding="utf-8") as logf:
        logf.write(f"==== {filename} ====\n")
        logf.write(translated + "\n\n")

    print(translated)


def load_cached_texts(cache_dir: str):
    texts = []
    filepaths = []
    
    for file in os.listdir(cache_dir):
        if file.endswith(".txt"):
            path = os.path.join(cache_dir, file)
            with open(path, "r", encoding="utf-8") as f:
                texts.append(f.read())
            filepaths.append(path)
    
    return texts, filepaths

# キャッシュされたテキストを読み込む
files = ["hasEDA"] # "noEDA","littleEDA",
target_dir = "result2/"
os.makedirs(target_dir,exist_ok=True)
for fl in files:
    cache_dir = f"PDF/cache/{fl}"  # ここを実際のディレクトリに置き換えて
    texts, paths = load_cached_texts(cache_dir)
    # 各テキストに対して EDA 推定を実行
    for i in range(5):
        log_file_path = f"{target_dir}{fl}{i+1}.txt"
        max_files = min(99,len(paths))
        readed = 0
        for text, path in zip(texts, paths):
            filename = os.path.basename(path)
            print(f"===={readed+1}/{max_files} {filename} ====")
            getEDA(text, log_file_path, filename)
            print("\n")
            readed += 1
            if readed >= max_files:
                break