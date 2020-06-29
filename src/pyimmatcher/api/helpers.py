from typing import Type, Callable

from pyimmatcher.api.results import make_message, BasicResult, TestResult
from pyimmatcher.api.assertions import T, Assertion, InvertedAssertion

__all__ = ['AsAssertion', 'ResultBuilder']



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


class ResultBuilder:
    """
    `ResultBuilder` provides easy ways to build a `TestResult` under the
    three most common circumstances:

    1) The test passes, and the 'actual' message would have nothing more specific
    to add that the 'expected' message didn't already convey. This is the
    'simple pass'
    2) The test passes, and the 'actual' message could add more specifics that
    the 'expected' message didn't convey. This is the normal 'pass'
    3) The test fails, so you definitely have something different to say in the
    'actual' message than in the 'expected' message

    This builder has a few advantages over directly creating `TestResult`s
    yourself:

    + You don't have to pass in a boolean and try to remember if it means 'pass'
    or 'fail'
    + You can set up the expected message once at the beginning of the test
    method and not have it infect the rest of the test code.
    + You don't have to worry about making the `Callable`s that return the
    final string messages. Instead the appropriate methods take a string to be
    formatted along with any formatting arguments. If you're providing a normal
    string, then it just created a function that returns that string.
    """
    def __init__(self, expected: str, *args, **kwargs):
        """
        Initialize the builder with the 'expected' message. If you simply pass
        in the string, it won't try to be formatted, but if you want to do a
        formatted string, you also pass in the arguments that you would pass
        into the `str.format()` method.
        :param expected: base 'expected' message, possibly to be formatted
        """
        self._expected = make_message(expected, *args, **kwargs)

    def simple_pass(self) -> TestResult:
        """
        If you have nothing to add to the 'actual' message and just want to
        reuse the 'expected' message as the 'actual' message, use this method
        to get the passing result.
        :return: simple, passing `TestResult` with the given message
        """
        return BasicResult(True, self._expected, self._expected)

    def pass_(self, actual: str, *args, **kwargs) -> TestResult:
        """
        Creates a passing result where the given string (and its optional
        formatting) is used for the 'actual' message, instead of the 'expected'
        message.
        :param actual: base 'actual' message, possibly to be formatted
        :param args: positional arguments to supply to the `format()` method
        :param kwargs: keyword arguments to supply to the `format()` method
        :return: passing `TestResult` with the given messages
        """
        _actual = make_message(actual, *args, **kwargs)
        return BasicResult(True, self._expected, _actual)

    def fail(self, actual: str, *args, **kwargs) -> TestResult:
        """
        Creates a failing result where the given string (and its optional
        formatting) is used for the 'actual' message, instead of the 'expected'
        message.
        :param actual: base 'actual' message, possibly to be formatted
        :param args: positional arguments to supply to the `format()` method
        :param kwargs: keyword arguments to supply to the `format()` method
        :return: failing `TestResult` with the given messages
        """
        _actual = make_message(actual, *args, **kwargs)
        return BasicResult(False, self._expected, _actual)


def not_(assertion: Assertion[T]) -> Assertion[T]:
    return InvertedAssertion(assertion)


