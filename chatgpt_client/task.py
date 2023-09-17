from dataclasses import dataclass
from typing import Any

TASKTYPE = [
    "Completion",
    "ChatCompletion",
    "Embedding",
    "Edit",
    "Image",
    "FineTune",
    "Mock",
]


@dataclass
class Task:
    id: str
    data: Any
    type: str
    model: str="gpt-3.5-turbo"
    response: Any=None
    done: bool=False
    max_retries: int=5
    failed_info: Any=None