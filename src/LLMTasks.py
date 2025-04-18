from __future__ import annotations
from pathlib import Path
from pathlib import Path
from typing import Sequence, Union

import openai

def load_prompt(path:Path) -> str:
    """
    load prompt in the path.
    """
    with open(path, "r") as f: return f.read()

def ask(instruction:str, user_prompt:str, model_name:str) -> str:
    """
    ask LLM to process `input` with `instruction`.
    """
    response = openai.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "developer", "content": instruction},
            {"role": "user", "content": user_prompt}
        ]
    )
    res = response.choices[0].message.content
    assert res
    return res

def ask_with_path(instr_path:Path, user_prompt:str, model_name:str) -> str:
    """
    ask LLM to process `input` with the prompt in `instr_path`.
    """
    developer_prompt = load_prompt(instr_path)
    return ask(developer_prompt, user_prompt, model_name)

class LLMTasks:
    paths: list[Path]
    model_name: str
    def __init__(
        self,
        path_or_paths: Union[str, list[Path]]
    ) -> None:
        """
        Initialize with a single path or a sequence of paths.
        """
        if isinstance(path_or_paths, list):
            self.paths = [p for p in path_or_paths]
        else:
            self.paths = [Path(path_or_paths)]

    def __or__(self, other: LLMTasks) -> LLMTasks:
        return LLMTasks(self.paths + other.paths)

    def execute(self, text: str, model_name:str) -> str:
        """
        Execute the pipeline: sequentially call ask_with_path for each stored path.
        """
        result: str = text
        for path in self.paths:
            result = ask_with_path(path, result, model_name)
        return result
