from abc import ABC, abstractmethod
from typing import Optional, Collection, TypeVar, Type

from pyimmatcher.api import AllOfTestResult, AnyOfTestResult, AllOfTestResult, AnyOfTestResult, \
    Assertion, NoneOfTestResult

__all__ = ['FailureMessageMaker', 'Tester', 'test_that']

SUT = TypeVar('SUT', contravariant=True)

class FailureMessageMaker(ABC):
    """
    A type to override if you don't like the default format of the failure
    messages in this library.
    """
    @abstractmethod
    def make_message(self, expected_message: str, actual_message: str) -> str:
        """
        Takes in the expected results part of the message and the actual results
        part of the message generated by a `TestResult` to be formatted into a
        full failure message.
        :param expected_message: string of the expected result of the failed test
        :param actual_message: string of the actual result of the failed test
        :return: fully formatted failure message string
        """
        raise NotImplementedError


class DefaultFailureMessageMaker(FailureMessageMaker):
    """
    Default failure message formatter with the format of

        Expected:
            <expected result>
        Actual:
            <actual result>

    """
    def make_message(self, expected_message: str, actual_message: str) -> str:
        # if the messages have multiple lines, we want them tabbed over to the
        # same point as the beginning of the message.
        expected = expected_message.replace('\n', '\n\t')
        actual = actual_message.replace('\n', '\n\t')
        return f"""
        Expected:
            {expected}
        Actual:
            {actual}"""


class Tester:
    """
    `Tester` is a class that houses the main assertion methods. There are two
    reasons why this is a class with a few methods rather than a few standalone
    functions:

    1) So that you can change the wording from 'test that...' to 'should be...',
    'assert that...', or whatever you want simply by reassigning the default
    instance (`test_that`) to a variable of your preferred wording.

    2) If you're not a big fan of the formatting of the error messages, you can
    make a different `Tester` with a different, custom `FailureMessageMaker` to
    put in a different format, if you'd like

    `Tester` is not intended to be subclassed, so doing so is at your own risk
    if any breaking changes are made.
    """
    def __init__(self, message_maker: FailureMessageMaker=DefaultFailureMessageMaker()):
        self.msg_maker = message_maker

    def __call__(self,
                 var_to_test: Type[SUT],
                 matcher: Assertion[SUT],
                 msg: Optional[str]=None, *args, **kwargs):
        """
        Runs a matcher and creates the output for failed tests.
        :param var_to_test: variable being tested by the `Assertion`
        :param matcher: `Assertion` used to test the variable
        :param msg: Override for the failure message. Can be written in a
        formattable string form and used with trailing arguments and keyword
        arguments to lazily create the full string only when the test fails.
        `var_to_test` is always passed in as the first ordinal argument to the
        formatting call. See `str.format()` for more details.
        :param args: Arguments to pass into the formattable string in `msg`, if any
        :param kwargs: Keyword arguments to pass into the formattable string in
        `msg`, if any
        """
        result = matcher.test(var_to_test)
        if result.failed:
            self._failure(var_to_test, result, msg, *args, **kwargs)



    def all(self,
            var_to_test: Type[SUT],
            matchers: Collection[Assertion[SUT]],
            msg: Optional[str]=None, *args, **kwargs):
        """
        Runs a series of matchers and creates the output for the tests if any
        failed.
        :param var_to_test: variable being tested by the `Assertion`
        :param matchers: Collection of `Assertion`s used to test the variable
        :param msg: Override for the failure message. Can be written in a
        formattable string form and used with trailing arguments and keyword
        arguments to lazily create the full string only when the test fails.
        `var_to_test` is always passed in as the first ordinal argument to the
        formatting call. See `str.format()` for more details.
        :param args: Arguments to pass into the formattable string in `msg`, if any
        :param kwargs: Keyword arguments to pass into the formattable string in
        `msg`, if any.
        """
        if len(matchers) == 0:
            raise AssertionError("Nothing is tested")
        results = AllOfTestResult(
            [matcher.test(var_to_test) for matcher in matchers])
        if results.failed:
            self._failure(var_to_test, results, msg, *args, **kwargs)

    def any(self,
            var_to_test: Type[SUT],
            matchers: Collection[Assertion[SUT]],
            msg: Optional[str]=None, *args, **kwargs):
        """
        Runs a series of matchers and creates the output for the tests if they
        all failed.
        :param var_to_test: variable being tested by the `Assertion`
        :param matchers: Collection of `Assertion`s used to test the variable
        :param msg: Override for the failure message. Can be written in a
        formattable string form and used with trailing arguments and keyword
        arguments to lazily create the full string only when the test fails.
        `var_to_test` is always passed in as the first ordinal argument to the
        formatting call. See `str.format()` for more details.
        :param args: Arguments to pass into the formattable string in `msg`, if any
        :param kwargs: Keyword arguments to pass into the formattable string in
        `msg`, if any.
        """
        if len(matchers) == 0:
            raise AssertionError("Nothing is tested")
        results = AnyOfTestResult(
            [matcher.test(var_to_test) for matcher in matchers])
        if results.failed:
            self._failure(var_to_test, results, msg, *args, **kwargs)

    def none(self,
                var_to_test: Type[SUT],
                matchers: Collection[Assertion[SUT]],
                msg: Optional[str] = None, *args, **kwargs
                ):
        if len(matchers) == 0:
            raise AssertionError("Nothing is tested")
        results = NoneOfTestResult(
            [matcher.test(var_to_test) for matcher in matchers])
        if results.failed:
            self._failure(var_to_test, results, msg, *args, **kwargs)

    def _failure(self, var_to_test, result, msg, *args, **kwargs):
        if msg:
            err_msg = msg.format(var_to_test, *args, **kwargs)
        else:
            err_msg = self.msg_maker.make_message(result.expected(), result.actual())
        raise AssertionError(err_msg)


test_that = Tester()
