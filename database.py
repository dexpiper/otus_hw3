"""
Database
"""
import redis
from datetime import timedelta
import logging

from cachetools import TTLCache


class RedisStore:

    def __init__(self, host: str = 'localhost', port: int = 6379,
                 db: int = 0, password: str or None = None,
                 socket_timeout: float or None = None,
                 ttl=timedelta(minutes=60).seconds,
                 logger=logging.getLogger(__name__)):
        """
        Init a RedisStore object.
        * By default, cache TTL set on 60 minutes.
        * Using default database num. 0, standart Redis port and
        localhost.
        """
        self.r = redis.Redis(host=host, port=port, db=db,
                             password=password,
                             socket_timeout=socket_timeout)
        self.cache = TTLCache(maxsize=10, ttl=ttl)
        self.logger = logger

    def cache_get(self, key: str) -> str:
        value = self.cache.get(key, None)
        if not value:
            self.logger.debug('Key not in cache, trying to get from db')
            try:
                value = self.r.get(key)
            except LookupError as exc:
                self.logger.error('Cannot get value from db: %s' % exc)
        return value.decode('utf-8') if isinstance(value, bytes) else value

    def cache_set(self, key: str, value: str):
        self.cache[key] = value

    def get(self, key: str) -> str:
        value: bytes = self.r.get(key)
        if value is None:
            raise LookupError(f'No key {key} in database')
        return value.decode('utf-8')

    def set(self, key: str, value: str) -> bool:
        return self.r.set(key, value)

    def delete(self, key: str) -> int:
        return self.r.delete(key)
