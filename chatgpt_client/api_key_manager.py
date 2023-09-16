import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from math import inf
from typing import List
from tenacity import RetryError, retry, retry_if_not_exception_type, stop_after_attempt, wait_fixed

import openai
from openai.error import AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)

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
            api_delay: int=25,
            ) -> None:
        """
        Initialize the api key manager

        check every api key and add valid key into self._key_pool

        Args:
            key_pool (List[str]): a list of api keys
            api_delay (int, optional): delay of api call for each api key. Defaults to 25.
        """
        logger.debug("Initialize api key manager...")
        self._key_pool: asyncio.Queue[ApiKey] = asyncio.Queue()
        self._api_delay: int = api_delay
        for api_key_val in key_pool: # TODO: check before or after
            api_key = ApiKey(api_key_val)
            self._key_pool.put_nowait(api_key)

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

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(25))
    def is_api_key_valid(self, api_key: ApiKey) -> bool: # FIXME: currently unavailable
        """
        test whether the api key is valid

        usually used in __init__

        Args:
            api_key (ApiKey): api key

        Returns:
            bool: valid or not
        """
        try:
            openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
        except (AuthenticationError, RateLimitError) as e:
            api_key.valid = False
            return False
        except Exception as e:
            logger.debug(f"Unexpected error: {e}")
            raise
        else:
            api_key.valid = True
            return True

    async def verify(self, api_key: ApiKey) -> bool: # FIXME: currently unavailable
        """
        A wrap to is_api_key_valid method

        async sleep to avoid RateLimitError

        Args:
            api_key (ApiKey): api key

        Returns:
            bool: valid or not
        """
        if api_key.last_use != None:
            sec_to_sleep = self._api_delay - (datetime.now() - api_key.last_use).seconds
            if sec_to_sleep > 0:
                await asyncio.sleep(sec_to_sleep)
        try:
            self.is_api_key_valid(api_key)
        except RetryError as e:
            logger.error(f"{api_key.val} seems to be invalid.")
