import asyncio
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

SECONDS_PER_MINUTE = 60

P = ParamSpec("P")
R = TypeVar("R")


class AsyncRateLimiter:
    def __init__(self, rpm: int = 60) -> None:
        self._rpm = rpm
        self._calls_at = []

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            while True:
                now = time.time()
                self._calls_at = [
                    c for c in self._calls_at if c > now - SECONDS_PER_MINUTE
                ]

                if len(self._calls_at) < self._rpm:
                    break

                wait_time = self._calls_at[0] + SECONDS_PER_MINUTE - now
                await asyncio.sleep(wait_time)

            self._calls_at.append(time.time())
            return func(*args, **kwargs)

        return wrapper
