import os
import unittest
from time import sleep
from unittest.mock import MagicMock

from database import RedisStore
from tests.utils import cases


class TestRedisStore(unittest.TestCase):

    def setUp(self):
        redis_url = os.environ.get('REDIS_URL', 'localhost:6379')
        host, port = redis_url.split(':')
        self.store = RedisStore(host=host, port=port, db=3, socket_timeout=0.3)

    def test_basic_init(self):
        self.assertTrue(isinstance(self.store.r, object))

    def test_set_item(self):
        self.assertTrue(self.store.set('Foo', 'bar'))

    def test_get_item(self):
        self.assertTrue(self.store.set('Foo', 'bar'))
        v = self.store.get('Foo')
        self.assertIsInstance(v, str)
        self.assertEqual(v, 'bar', f'{v} is not "bar"')

    @cases(['boo!', 'spamspam', 'Spanish Inquisition'])
    def test_get_non_existent_item(self, key):
        with self.assertRaises(LookupError) as cm:
            self.store.get(key)
        self.assertIn('No key', str(cm.exception))

    def test_cache_set(self):
        store = RedisStore(db=3)
        store.cache_set('eggs', 'spam')
        self.assertEqual(store.cache['eggs'], 'spam')

    def test_cache_ttl_check(self):
        """
        TTL explicitly set in 1 sec
        """
        short_cache_store = RedisStore(db=3, ttl=1)
        short_cache_store.cache_set('breakfast', 'eggs')
        self.assertEqual(
            short_cache_store.cache.get('breakfast'),
            'eggs'
        )
        sleep(1)  # after 1 sec value should be flushed off
        self.assertIsNone(
            short_cache_store.cache.get('breakfast')
        )

    def test_cache_get_from_db_natural(self):
        """
        Store.cache_get() can only take 'Foo' from db, not from cache
        """
        self.assertTrue(self.store.set('Foo', 'bar'))
        self.assertEqual(self.store.cache_get('Foo'), 'bar')

    def test_cache_get_from_db_mock(self):
        """
        Retry previous test with mock: the cache calls 'real' db
        if it cannot find value
        """
        self.store.r.get = MagicMock(return_value='value')
        value = self.store.cache_get('foo')
        self.assertEqual(value, 'value')
        self.store.r.get.assert_called_once_with('foo')

    def test_cache_get_from_cache(self):
        """
        Vice versa: the cache should NOT call 'real' db
        """
        self.store.cache_set('SomeKey', 'spam')
        self.store.r.get = MagicMock(return_value=LookupError('Not expected'))
        v = self.store.cache_get('SomeKey')
        self.assertEqual(v, 'spam')
        self.store.r.get.assert_not_called()

    def tearDown(self):
        self.store.r.flushdb()
        self.store.cache.flushdb()
