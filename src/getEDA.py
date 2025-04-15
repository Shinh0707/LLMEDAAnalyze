import openai
import os

P = "secrets/.OPENAI_API_KEY"
with open(P, "r") as f:
    openai.api_key = f.read().strip()
 

def getEDA(text: str):
    instruction = '''
# Prior Knowledge
    Entertainment Design Assets (EDA) in content refer to expressions that describe the "emotional responses" intended to be evoked in players, as defined in the content's design requirements.
    However, EDA here specifically refers to "mechanisms that directly cause changes in the user's own emotional state."

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
    - "The emotional responses targeted in the user are clearly defined as part of the design requirements of the content."
        - It is important that they are specifically and unambiguously defined by the developers.
        - If the emotional experience varies based on user behavior (i.e., the EDA becomes optional), this condition is not satisfied.
    - "The content aims to deliberately influence the user's own emotional state."
    - "The paper discusses what kind of emotional response the content is expected to evoke when used."

# Response Format
    Please answer in the form of a JSON block like the following:
    ```
    {
        "Design Targeted EDA Reason": string, // Reason for Design Targeted EDA
        "Design Targeted EDA": boolean, // Whether the emotional response is clearly specified in the content design requirements
        "Propose EDA Reason": string, // Reason for Propose EDA
        "Propose EDA": boolean, // Whether the content aims to influence the user's emotional state
        "Analyze EDA Reason": string, // Reason for Analyze EDA
        "Analyze EDA": boolean, // Whether the paper discusses the emotional response evoked by using the content
        "Clarity Score reason": string, // Reason for the Clarity Score
        "Clarity Score": int, // 4: EDA is a clear main topic, 3: EDA is a main topic but unclear, 2: Not a main topic, 1: No EDA at all
        "EDA": string[], // Direct quotes from the paper describing the targeted emotional responses (leave empty if none)
    }
    ```
    '''
    
    response = openai.chat.completions.create(
        model="o3-mini-2025-01-31",
        messages=[
            {"role": "developer", "content": instruction},
            {"role": "user", "content": text}
        ]
    )
    # モデルからの応答を出力
    # print(response.choices[0].message.content)

    res = response.choices[0].message.content
    response = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "developer", "content": "このJSONのKeyをそのままで、Key=EDAのValue以外のValueの英語を日本語訳してJSON形式で回答して。"},
            {"role": "user", "content": res}
        ]
    )

    print(response.choices[0].message.content)

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
cache_dir = "PDF/cache/littleEDA"  # ここを実際のディレクトリに置き換えて
texts, paths = load_cached_texts(cache_dir)

# 各テキストに対して EDA 推定を実行
max_files = min(4,len(paths))
readed = 0
for text, path in zip(texts, paths):
    print(f"===={readed+1}/{max_files} {os.path.basename(path)} ====")
    getEDA(text)
    print("\n")
    readed += 1
    if readed >= max_files:
        break