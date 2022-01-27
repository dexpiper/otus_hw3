"""
Database
"""
import redis
from datetime import timedelta
import logging
import time


class RedisStore:

    def __init__(self, host: str = 'localhost', port: int = 6379,
                 db: int = 0, password: str or None = None,
                 socket_timeout: float or None = 0.5,
                 ttl=timedelta(minutes=60).seconds,
                 max_retry=3, connect: bool = True,
                 logger=logging.getLogger(__name__)):
        """
        Init a RedisStore object.
        * By default, cache TTL set on 60 minutes.
        * Using default database num. 0, standart Redis port and
        localhost.
        """
        self.host = host
        self.port = port
        self.db = db
        self.db_cache = db + 1
        self.password = password
        self.socket_timeout = socket_timeout
        self.logger = logger
        self.ttl = ttl
        self.max_retry = max_retry
        if connect:
            self.r = self._connect(self.db)
            self.cache = self._connect(self.db_cache)

    def _connect(self, db):
        return redis.Redis(host=self.host, port=self.port, db=db,
                           password=self.password,
                           socket_timeout=self.socket_timeout,
                           decode_responses=True)

    def ping_reconnect(self, storage, db, store_name='storage'):
        try:
            conn = storage.ping()
        except redis.exceptions.ConnectionError:
            self.logger.info(f'Cannot connect to {store_name}. Reconnecting')
            for _ in range(self.max_retry):
                try:
                    storage = self._connect(db)
                    conn = storage.ping()
                except:  # noqa E722 (flake8 enable bare except)
                    time.sleep(1)
            if not conn:
                raise ConnectionError('Cannot connect to cache')

    def cache_get(self, key: str) -> str:
        self.ping_reconnect(self.cache, self.db_cache)
        value = self.cache.get(key) or None
        if not value:
            self.logger.debug('Key not in cache, trying to get from db')
            try:
                value = self.r.get(key)
            except LookupError as exc:
                self.logger.error('Cannot get value from db: %s' % exc)
        return value

    def cache_set(self, key: str, value: str):
        self.ping_reconnect(self.cache, self.db_cache)
        self.cache.set(key, value, ex=self.ttl)

    def get(self, key: str) -> str:
        self.ping_reconnect(self.r, self.db)
        value = self.r.get(key)
        if value is None:
            raise LookupError(f'No key {key} in database')
        return value

    def set(self, key: str, value: str) -> bool:
        self.ping_reconnect(self.r, self.db)
        return self.r.set(key, value)

    def delete(self, key: str) -> int:
        self.ping_reconnect(self.r, self.db)
        return self.r.delete(key)
