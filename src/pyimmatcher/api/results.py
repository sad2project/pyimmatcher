from abc import ABC
from typing import Callable, List


Message = Callable[[], str]


class TestResult(ABC):
    """
    `TestResult` is a result from a test, obviously. They're created by the
    `test()` method on `NegatableAssertion` (usually) and have serve two basic needs:

    1) Let the assertion function know whether or not the test failed
    2) Provide the expected and actual messages for displaying how a test failed

    In the Hamcrest library, the `Matchers` provided all of this. Doing so
    required the object to be mutable if the 'actual result' message had any
    specifics from the object being tested because it would have to save that
    object on the instance during the testing phase, rather than getting it
    in the constructor. On top of that, the failure message was done via
    mutating an argument rather than returning something.

    I like to lean towards purer functions and types, which allow you to reuse
    the `NegatableAssertion` instances and make the result message code cleaner, I think.

    Something that is probably unexpected about `TestResult` is that the
    *expected* and *actual* messages are functions that return a string rather
    than just being a string in and of themselves. This is because, if the
    `NegatableAssertion` wants to use a formatted string as part of the output, it's not
    worth the effort of doing that formatting if the test doesn't fail and need
    the failure message.

    We still collect the information on a passing test though, because it may be
    part of a collection of results (such as AnyOfTestResult or AllOfTestResult)
    that wants to output from a passing result because of an overall failure.
    """
    passed: bool
    expected: Callable[[], str]
    actual: Callable[[], str]

    @property
    def failed(self):
        return not self.passed


class BasicResult(TestResult):
    """
    `BasicResult` is the basic, obvious implementation of `TestResult`. The best
    way to create a `BasicResult` is by using the
    `pyimmatcher.api.ResultBuilder` class.
    """
    def __init__(self,
            passed: bool,
            expected: Message,
            actual: Message):
        self.passed = passed
        self.expected = expected
        self.actual = actual


def _make_simple_message(string: str) -> Message:
    """
    Makes a message function that simply returns the given string
    """
    def message() -> str:
        return string
    return message


def _make_message(string: str, *args, **kwargs) -> Message:
    """
    Makes a message function that uses the given arguments in a `str.format()`
    call
    """
    def message() -> str:
        return string.format(*args, **kwargs)
    return message


def make_message(string: str, *args, **kwargs) -> Message:
    """
    Creates a callable with no parameters that returns the given string as if it
    had called `format()` with the other given arguments. In other words, it
    creates a lazily formatted string
    :param string: string to be formatted
    :param args: positional arguments to supply to the `format()` method
    :param kwargs: keyword arguments to supply to the `format()` method
    :return: formatted version of the given string
    """
    if len(args) == 0 and len(kwargs) == 0:
        return _make_simple_message(string)
    else:
        return _make_message(string, *args, **kwargs)


class MultiTestResult(TestResult):
    def __init__(self, results: List[TestResult]):
        self._results = results

    def actual(self):
        return "\nAND ".join(result.actual() for result in self._results if result.failed)


class AllOfTestResult(MultiTestResult):
    """
    Used by `Tester.all()` to collect all the `TestResult`s from its `NegatableAssertion`s and
    make them into a combined result.

    The 'actual' message only returns the 'actual' messages from the failed
    `TestResult`s in order to zero in on the problems. But (and I went back and
    forth on this a lot) the 'expected' message *does* list off all of the
    'expected' messages, not just the failed ones. This is to give the full
    context of what's being tested.
    """
    def __init__(self, results: List[TestResult]):
        super().__init__(results)

    @property
    def passed(self):
        return all(result.passed for result in self._results)

    def expected(self):
        return "\nAND ".join(result.expected() for result in self._results)


class AnyOfTestResult(MultiTestResult):
    """
    Used by `Tester.any()` to collect all the `TestResult`s from its `NegatableAssertion`s and
    make them into a combined result.
    """
    def __init__(self, results: List[TestResult]):
        super().__init__(results)

    @property
    def passed(self):
        return any(result.passed for result in self._results)

    def expected(self):
        return "\nOR ".join(result.expected() for result in self._results)


class NoneOfTestResult(MultiTestResult):
    def __init__(self, results: List[TestResult]):
        super().__init__(results)

    @property
    def passed(self):
        return not any(result.passed for result in self._results)

    def expected(self):
        return "NEITHER " + "\nNOR ".join(result.expected() for result in self._results)


def invert(result: TestResult):
    return BasicResult(result.failed,
                       make_message("not {}", result.expected()),
                       result.actual)
