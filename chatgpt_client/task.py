from dataclasses import dataclass
from typing import Any

TASKTYPE = [
    "Completion",
    "ChatCompletion",
    "Embedding",
    "Edit",
    "Image",
    "FineTune",
]


@dataclass
class Task:
    id: str
    data: Any
    type: str
    model: str="gpt-3.5-turbo"
    response: Any=None
    done: bool=False