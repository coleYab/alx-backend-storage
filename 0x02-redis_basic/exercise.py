#!/usr/bin/env python3
"""
exercise: implementation for the class
"""


import uuid
import typing
from functools import wraps
import redis


def count_calls(fn: typing.Callable) -> typing.Callable:
    """
    count_calls: function wrappers to count how many times
        the function fn is called.
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        """
        wrapper function
        """
        fn_name = fn.__qualname__
        called_times = self._redis.get(fn_name)
        if called_times is None:
            self._redis.set(fn_name, 1)
        else:
            self._redis.incr(fn_name)
        return fn(self, *args, **kwargs)

    return wrapper


def call_history(fn: typing.Callable):
    """
    call_history: stores the input and the output arguments for the function
    to be called
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        """
        wrapper: the main wrapper login
        """
        fn_name = fn.__qualname__
        self._redis.rpush(f"{fn_name}:inputs", str(args))
        res = fn(self, *args, **kwargs)
        self._redis.rpush(f"{fn_name}:outputs", res)
        return res
    return wrapper


class Cache:
    """
    Caching implementation class
    """
    def __init__(self):
        """
        constructor: will create a fresh instance of redis.
        """
        self._redis = redis.Redis(host="localhost", port="6379",
                                  decode_responses=True)
        self._redis.flushdb()

    @call_history
    def store(self, data: typing.Union[str, bytes, int, float]) -> str:
        """
        store: method to store a given data by generataing a uuid, as a key
        for that specific data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    @count_calls
    def get(self, key: str, fn: typing.Optional[typing.Callable] = None):
        """
        get::(key, fn) -> the basic readed string or fn(readed_string)
        """
        data = self._redis.get(key)
        if data is None:
            return data

        data = bytes(data, encoding='utf-8')
        return data if fn is None else fn(data)

    def get_int(self, key: int):
        """
        returns: self.get(key, int)
        """
        return self.get(key, int)

    def get_str(self, key: str):
        """
        returns: self.get(key, str)
        """
        return self.get(key, str)

    def replay(self, fn):
        """
        replay: function to replay the cached data of the function.
        """
        fn_name = fn.__qualname__
        fn_inputs = self._redis.lrange(f'{fn_name}:inputs', 0, -1)
        fn_outputs = self._redis.lrange(f'{fn_name}:outputs', 0, -1)
        print(f"{fn_name} was called {len(fn_inputs)} times:")
        for inp, outp in zip(fn_inputs, fn_outputs):
            print(f"{fn_name}(*{inp}) -> {outp}")
