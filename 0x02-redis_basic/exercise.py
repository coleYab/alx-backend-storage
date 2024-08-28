#!/usr/bin/env python3
"""
exercise: implementation for the class
"""


import uuid
import typing
from functools import wraps
import redis


def count_calls(method: typing.Callable) -> typing.Callable:
    """
    count_calls: function wrappers to count how many times
        the function method is called.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        wrapper function
        """
        method_name = method.__qualname__
        called_times = self._redis.get(method_name)
        if called_times is None:
            self._redis.set(method_name, 1)
        else:
            self._redis.incr(method_name)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: typing.Callable):
    """
    call_history: stores the input and the output arguments for the function
    to be called
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        wrapper: the main wrapper login
        """
        method_name = method.__qualname__
        self._redis.rpush(f"{method_name}:inputs", str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(f"{method_name}:outputs", res)
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
    @count_calls
    def store(self, data: typing.Union[str, bytes, int, float]) -> str:
        """
        store: method to store a given data by generataing a uuid, as a key
        for that specific data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    @count_calls
    def get(self, key: str, method: typing.Optional[typing.Callable] = None):
        """
        get::(key, method) -> the basic readed string or method(readed_string)
        """
        data = self._redis.get(key)
        if data is None:
            return data

        data = bytes(data, encoding='utf-8')
        return data if method is None else method(data)

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

    def replay(self, method):
        """
        replay: function to replay the cached data of the function.
        """
        method_name = method.__qualname__
        method_inputs = self._redis.lrange(f'{method_name}:inputs', 0, -1)
        method_outputs = self._redis.lrange(f'{method_name}:outputs', 0, -1)
        print(f"{method_name} was called {len(method_inputs)} times:")
        for inp, outp in zip(method_inputs, method_outputs):
            print(f"{method_name}(*{inp}) -> {outp}")
