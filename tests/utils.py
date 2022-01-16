"""
Test case decorator
"""
import functools
from typing import Callable, Any


def cases(cases: list):
    """
    Test parametrization with failed case alert.
    Usage:
    @cases(['value1', 'value2', ...])
    def test_check_values(self, value):
        pass
    """
    def decorator(f: Callable):
        @functools.wraps(f)
        def wrapper(*args: tuple or Any):
            self = args[0]
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                with self.subTest(case=c):
                    f(*new_args)
        return wrapper
    return decorator
