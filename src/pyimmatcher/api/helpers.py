from typing import Type, Callable

from pyimmatcher.api.results import TestResult
from pyimmatcher.api.assertions import T, Assertion

__all__ = ['AsAssertion', 'not_']


class AsAssertion(Assertion[T]):
    """
    `AsAssertion` is a decorator that turns a function that matches the
    `Assertion.test()` method signature and turns it into a `Assertion`.

    This is only helpful with non-parameterized Tests, such as "is not none".
    """
    def __init__(self, matcher_func: Callable[[T], TestResult]):
        self.func = matcher_func

    def __call__(self):
        return self

    def test(self, actual: Type[T]) -> TestResult:
        return self.func(actual)


def not_(assertion: Assertion[T]) -> Assertion[T]:
    return ~assertion


def tabbed(not_tabbed: str):
    return '\t' + not_tabbed.replace('\n', '\n\t')
