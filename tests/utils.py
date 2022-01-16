"""
Test case decorator
"""
import functools


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            self = args[0]
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                with self.subTest(case=c):
                    f(*new_args)
        return wrapper
    return decorator
