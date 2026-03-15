"""Retry utilities"""

import asyncio
import functools
from typing import Callable, TypeVar, Any

T = TypeVar('T')


def retry(max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator for retrying async functions"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
            raise last_exception

        return wrapper
    return decorator


def retry_sync(max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator for retrying sync functions"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            import time
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
            raise last_exception

        return wrapper
    return decorator
