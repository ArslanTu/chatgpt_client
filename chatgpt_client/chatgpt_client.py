import asyncio
import logging
from datetime import datetime
from typing import List

import openai
from openai.error import AuthenticationError, RateLimitError
from tenacity import (AsyncRetrying, retry_if_not_exception_type,
                      stop_after_attempt)

from .api_key_manager import ApiKeyManager
from .error import KeyInvalidError, NoValidKeyError
from .task import Task

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class ChatGPTClient:
    def __init__(
            self, 
            api_key_pool: List[str],
            api_base: str="https://api.openai.com/v1",
            api_delay: int=25,
            invalid_api_key_path: str='./invalid_api_keys.txt',
            ) -> None:
        self._api_key_manager: ApiKeyManager = ApiKeyManager(api_key_pool, invalid_api_key_path)
        self._api_base: str = api_base
        self._api_delay: int = api_delay
    
    async def execute_single_task(self, task: Task) -> Task:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(task.max_retries),
                retry=retry_if_not_exception_type((NotImplementedError, ValueError, NoValidKeyError)),
                reraise=True,
            ):
                with attempt:
                    # 1. 尝试获取 key
                    try:
                        # 循环等待，若超时则检查可用key数量，从而决定继续等待还是 raise error
                        while True:
                            try:
                                api_key = await asyncio.wait_for(self._api_key_manager.get(), timeout=5)
                                break
                            except asyncio.exceptions.TimeoutError:
                                lock = asyncio.Lock()
                                async with lock:
                                    total_api_key_num = self._api_key_manager._total_api_key_num
                                if total_api_key_num < 1:
                                    raise NoValidKeyError("No valid key.")
                                else:
                                    continue
                            except Exception:
                                raise
                        # 拿到 key，休眠
                        time_to_sleep = self._api_delay - (datetime.now() - api_key.last_use).seconds if api_key.last_use is not None else -1
                        if time_to_sleep > 0:
                            await asyncio.sleep(time_to_sleep)
                    # 没有可用 key，不重试
                    except NoValidKeyError as e:
                        task.failed_info = e.__str__()
                        raise
                    # 其他异常
                    except Exception:
                        raise
                    
                    # 2. 尝试处理任务
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
                    # 不可重试
                    except (NotImplementedError, ValueError) as e:
                        task.failed_info = e.__str__()
                        raise
                    # 可重试
                    # key 失效则不放回，而是记录，并减少可用 key 数量，然后重试
                    # 否则要将 key 放回并重试
                    except RateLimitError as e:
                        task.failed_info = e.__str__()
                        # 余额不足
                        if e.__str__() == "You exceeded your current quota, please check your plan and billing details.":
                            await self._api_key_manager.record_invalid_api_key(api_key)
                            lock = asyncio.Lock()
                            async with lock:
                                self._api_key_manager._total_api_key_num -= 1
                            raise KeyInvalidError
                        # 频率过高，不更新使用时间 # FIXME: it may need an update
                        else:
                            await self._api_key_manager.put(api_key)
                            raise
                    # key 不可用
                    except AuthenticationError as e:
                        task.failed_info = e.__str__()
                        await self._api_key_manager.record_invalid_api_key(api_key)
                        lock = asyncio.Lock()
                        async with lock:
                            self._api_key_manager._total_api_key_num -= 1
                        raise KeyInvalidError
                    # 其他异常
                    except Exception:
                        raise
                    # 无异常，更新 task，更新 key 的使用时间
                    else:
                        api_key.last_use = datetime.now()
                        task.response = response
                        task.done = True
        # 需要中断的异常
        except(NotImplementedError, ValueError) as e:
            raise

        # 重试达到上限时仍然报 KeyInvalidError 或 RateLimitError
        # FIXME: should retry until no key in pool, or only retry for task.max_retries
        except KeyInvalidError:
            logger.exception("Too much invalid keys.")
        except RateLimitError:
            logger.debug("Retry limit exceed.")

        except NoValidKeyError as e:
            logger.debug(e)

        # 其他异常，需要中断
        except Exception:
            raise

        # 无异常或非中断异常，返回 task
        return task


    async def execute_tasks(self, tasks: List[Task]) -> List[Task]:
        tasks_to_execute = []
        for task in tasks:
            task_to_execute = asyncio.create_task(self.execute_single_task(task))
            tasks_to_execute.append(task_to_execute)
        results = await asyncio.gather(*tasks_to_execute)
        return results