from httpx import ReadTimeout

def readtimeout_retry(count: int):
    def decorator(httpx_function):
        async def wrapper(*args, **kwargs):
            for attempt in range(count):
                try:
                    res = await httpx_function(*args, **kwargs)
                    return res
                except ReadTimeout as e:
                    if attempt + 1 < count:
                        continue
                    else:
                        raise e

        return wrapper

    return decorator
