#!/usr/bin/enb python3

"""
get_web_data: a simple page that will help us to retrive a web api
"""

import typing
from functools import wraps
import requests
import redis

_redis_db = redis.Redis()
_redis_db.flushdb()

def cache_request(get_page: typing):
    @wraps(get_page)
    def wrapper(url, *args, **kwargs):
        key = f"count: {url}"
        val = None
        try:
            val = get_page(*args, **kwargs)
            count = _redis_db.get(key)
            if count is not None:
                _redis_db.setex(key, 10, 1 + count)
            else:
                _redis_db.setex(key, 10, 1)
        except:
            pass
        return val

    return wrapper

def get_page(url: str) -> str:
    res = requests.get(url, timeout=10)
    return res



