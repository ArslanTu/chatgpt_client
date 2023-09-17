import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from math import inf
from typing import List

import aiofiles

logger = logging.getLogger(__name__)

NO_VALID_API_KEY="no_valid_api_key"

@dataclass
class ApiKey:
    """
    A dataclass for api key
    """
    val: str # api_key value
    balance: float=inf # account balance, invalid now
    valid: bool=True # whether is valid
    last_use: datetime=None # the time last used


class ApiKeyManager:
    def __init__(
            self, 
            key_pool: List[str], 
            invalid_api_key_path: str,
            ) -> None:
        """
        Initialize the api key manager

        Args:
            key_pool (List[str]): a list of api keys
        """
        logger.debug("Initialize api key manager...")
        self._key_pool: asyncio.Queue[ApiKey] = asyncio.Queue()
        for api_key_val in key_pool:
            api_key = ApiKey(api_key_val)
            self._key_pool.put_nowait(api_key)
        self._total_api_key_num: int = self._key_pool.qsize()
        self._invalid_api_key_path: str = invalid_api_key_path

        if os.path.exists(self._invalid_api_key_path):
            os.remove(self._invalid_api_key_path)

    async def get(self) -> ApiKey:
        """
        async get an api key

        Returns:
            ApiKey: api key
        """
        api_key = await self._key_pool.get()
        self._key_pool.task_done()
        return api_key

    async def put(self, api_key: ApiKey) -> None:
        """
        async put back api key into api key manager

        Args:
            api_key (ApiKey): api key
        """
        await self._key_pool.put(api_key)

    async def record_invalid_api_key(self, api_key: ApiKey) -> None:
        api_key_val = api_key.val
        async with aiofiles.open(self._invalid_api_key_path, 'a') as f:
            await f.write(api_key_val + '\n')