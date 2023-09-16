import asyncio
import logging
from datetime import datetime
from typing import List

import openai

from .api_key_manager import ApiKeyManager
from .task import Task

logger = logging.getLogger(__name__)

class ChatGPTClient:
    def __init__(
            self, 
            api_key_pool: List[str],
            api_base: str="https://api.openai.com/v1",
            api_delay: int=25,
            ) -> None:
        self._api_key_manager: ApiKeyManager = ApiKeyManager(api_key_pool, api_delay)
        self._api_base: str = api_base
        self._api_delay = api_delay
    
    async def execute_task(self, task: Task) -> Task:
        api_key = await self._api_key_manager.get()
        time_to_sleep = self._api_delay - (datetime.now() - api_key.last_use).seconds if api_key.last_use is not None else -1
        if  time_to_sleep > 0:
            await asyncio.sleep(time_to_sleep)
        try:
            match task.type:
                case "Completion":
                    raise NotImplementedError(f"Not implemented task type: {task.type}")
                case "ChatCompletion":
                    response = await openai.ChatCompletion.acreate(
                        model=task.model, 
                        messages=task.data,
                        api_key=api_key.val,
                        api_base=self._api_base,
                        )
                case "Embedding":
                    raise NotImplementedError(f"Not implemented task type: {task.type}")
                case "Edit":
                    raise NotImplementedError(f"Not implemented task type: {task.type}")
                case "Image":
                    raise NotImplementedError(f"Not implemented task type: {task.type}")
                case "FineTune":
                    raise NotImplementedError(f"Not implemented task type: {task.type}")
                case "Mock":
                    response = "Success!"
                case _:
                    raise ValueError(f"Wrong task type: {task.type}")
        except Exception as e:
            logger.error(f"{e} at task id: {task.id}")
        else:
            task.response = response
            task.done = True
        finally:
            api_key.last_use = datetime.now()
            await self._api_key_manager.put(api_key)
            return task

    async def execute_tasks(self, tasks: List[Task]) -> List[Task]:
        tasks_to_execute = []
        for task in tasks:
            task_to_execute = asyncio.create_task(self.execute_task(task))
            tasks_to_execute.append(task_to_execute)
        results = await asyncio.gather(*tasks_to_execute)
        return results
