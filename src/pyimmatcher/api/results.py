from abc import ABC
from typing import Callable, List


Message = Callable[[], str]


class TestResult(ABC):
    """
    `TestResult` is a result from a test, obviously. They're created by the
    `test()` method on `Assertion` (usually) and have serve two basic needs:

    1) Let the assertion function know whether the test failed
    2) Provide the messages for displaying how a test failed (both normally or
        negated)

    In the Hamcrest library, the `Matchers` provided all of this. Doing so
    required the object to be mutable if the 'actual result' message had any
    specifics from the object being tested because it would have to save that
    object on the instance during the testing phase, rather than getting it
    in the constructor. On top of that, the failure message was done via
    mutating an argument rather than returning something.

    I like to lean towards purer functions and types, which allow you to reuse
    the `Assertion` instances and make the result message code cleaner, I think.

    Something that is probably unexpected about `TestResult` is that the
    *expected* and *actual* messages are functions that return a string rather
    than just being a string in and of themselves. This is because, if the
    `Assertion` wants to use a formatted string as part of the output, it's not
    worth the effort of doing that formatting if the test doesn't fail and need
    the failure message.

    We still collect the information on a passing test though, because it may be
    part of a collection of results (such as AnyOfTestResult or AllOfTestResult)
    that wants to output from a passing result because of an overall failure.
    """
    passed: bool
    failure_message: Callable[[], str]
    negated_message: Callable[[], str]

    @property
    def failed(self):
        return not self.passed

    def __not__(self) -> TestResult:
        return NegatedResult(self)


class BasicResult(TestResult):
    """
    `BasicResult` is the basic, obvious implementation of `TestResult`. The best
    way to create a `BasicResult` is by using the
    `pyimmatcher.api.ResultBuilder` class.
    """
    def __init__(self,
            passed: bool,
            failure_message: Message,
            negated_message: Message):
        self.passed = passed
        self.failure_message = failure_message
        self.negated_message = negated_message


class NegatedResult(TestResult):
    def __init__(self, original: TestResult):
        self.original: TestResult = original

    def __new__(cls, original):
        """
        If the original Result that we're wrapping is already a NegatedResult, simply return that Result's wrapped
        Result.
        :param original: Result that we're wrapping
        """
        if isinstance(original, NegatedResult):
            return original.original
        else:
            return super().__new__(original, *args, **kwargs)

    @property
    def passed(self):
        return not self.original.passed

    @property
    def failure_message(self):
        return self.original.negated_message

    @property
    def negated_message(self):
        return self.original.failure_message

    def __not__(self):
        return self.original



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

    def failure_message(self):
        return "\nAND ".join(result.failure_message() for result in self._results if result.failed)

    def negated_message(self):
        return "\nAND ".join(result.negated_message() for result in self._results if result.passed)


class AllOfTestResult(MultiTestResult):
    """
    Used by `Tester.all()` to collect all the `TestResult`s from its `NegatableAssertion`s and
    make them into a combined result.

    The 'actual' message only returns the 'actual' messages from the failed
    `TestResult`s in order to zero in on the problems. But (and I went back and
    forth on this a lot) the 'expected' message *does* list off all the
    'expected' messages, not just the failed ones. This is to give the full
    context of what's being tested.
    """
    def __init__(self, results: List[TestResult]):
        super().__init__(results)

    @property
    def passed(self):
        return all(result.passed for result in self._results)

    def failure_message(self):
        return "Some assertions failed:\n" + super().failure_message()

    def negated_message(self):
        return "Every assertion passed when at least one was expected to fail"


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

    def failure_message(self):
        return "Every assertion failed: \n" + super().failure_message()

    def negated_message(self):
        return "Some assertions passed: \n" + super().negated_message()

    def __not__(self) -> TestResult:
        return NoneOfTestResult(self._results)


class NoneOfTestResult(MultiTestResult):
    def __init__(self, results: List[TestResult]):
        super().__init__(results)

    @property
    def passed(self):
        return not any(result.passed for result in self._results)

    def failure_message(self):
        return "Some assertions passed:\n" + super().negated_message()

    def negated_message(self):
        return "Every assertion failed: \n" + super().failure_message()

    def __not__(self) -> TestResult:
        return AnyOfTestResult(self._results)


def negate(result: TestResult):
    return NegatedResult(result)
