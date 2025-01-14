from typing import Optional, Any, List, Type

import httpx
from httpcore import ConnectError, TimeoutException


class ResilientHttpClient:
    def __init__(self, max_attempts: int = 3, timeout: Optional[float] = 10.0, retry_on: Optional[List[Type[Exception]]] = None):
        self.max_attempts = max_attempts
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)
        self.retry_on = retry_on or [ConnectError, TimeoutException]

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        attempts = 0
        while attempts <= self.max_attempts:
            try:
                print("attempt number {}".format(attempts+1))
                response = await self.client.request(method, url, **kwargs)
                #Raise errors to handle them differently
                response.raise_for_status()
                return response
            #Add 1 attempt if it is an allowed error to retry on
            except tuple(self.retry_on) as e:
                attempts += 1
                if attempts >= self.max_attempts:
                    raise e
            except httpx.HTTPStatusError as e:
                raise e

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)

    async def close(self):
        await self.client.aclose()