import time
from functools import wraps

_cache: dict[str, tuple[float, any]] = {}


def async_ttl_cache(ttl_seconds: int = 60):
    """Decorator that caches an async function's result for ttl_seconds,
    keyed by the function name + its arguments."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build a unique cache key from function name + arguments
            key = f"{func.__name__}:{args}:{kwargs}"

            now = time.time()
            if key in _cache:
                cached_time, cached_value = _cache[key]
                if now - cached_time < ttl_seconds:
                    return cached_value  # still fresh, reuse it

            # Not cached, or expired — call the real function
            result = await func(*args, **kwargs)
            _cache[key] = (now, result)
            return result

        return wrapper

    return decorator