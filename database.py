"""
Database
"""
import redis
from datetime import timedelta
import logging


class RedisStore:

    def __init__(self, host: str = 'localhost', port: int = 6379,
                 db: int = 0, password: str or None = None,
                 socket_timeout: float or None = None,
                 ttl=timedelta(minutes=60).seconds,
                 logger=logging.getLogger(__name__),
                 connect: bool = True):
        """
        Init a RedisStore object.
        * By default, cache TTL set on 60 minutes.
        * Using default database num. 0, standart Redis port and
        localhost.
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.socket_timeout = socket_timeout
        self.logger = logger
        self.ttl = ttl
        if connect:
            self._connect()

    def _connect(self):
        self.r = redis.Redis(host=self.host, port=self.port, db=self.db,
                             password=self.password,
                             socket_timeout=self.socket_timeout)
        self.cache = redis.Redis(host=self.host, port=self.port, db=self.db+1,
                                 password=self.password,
                                 socket_timeout=self.socket_timeout)

    def cache_get(self, key: str) -> str:
        value: bytes = self.cache.get(key) or None
        if not value:
            self.logger.debug('Key not in cache, trying to get from db')
            try:
                value = self.r.get(key)
            except LookupError as exc:
                self.logger.error('Cannot get value from db: %s' % exc)
        return value.decode('utf-8') if isinstance(value, bytes) else value

    def cache_set(self, key: str, value: str):
        self.cache.set(key, value, ex=self.ttl)

    def get(self, key: str) -> str:
        value: bytes = self.r.get(key)
        if value is None:
            raise LookupError(f'No key {key} in database')
        return value.decode('utf-8')

    def set(self, key: str, value: str) -> bool:
        return self.r.set(key, value)

    def delete(self, key: str) -> int:
        return self.r.delete(key)
