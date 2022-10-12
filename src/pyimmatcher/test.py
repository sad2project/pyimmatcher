from abc import ABC, abstractmethod
from typing import Optional, Collection, TypeVar, Type
from contextlib import contextmanager

from pyimmatcher.api import Assertion, AllOfTestResult, AnyOfTestResult, NoneOfTestResult, make_message

__all__ = ['Tester', 'test_that']

SUT = TypeVar('SUT', contravariant=True)


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

    `Tester` is not intended to be subclassed, doing so is at your own risk
    if any breaking changes are made.
    """

    def __call__(self,
                 var_to_test: Type[SUT],
                 matcher: Assertion[SUT],
                 msg: Optional[str]=None, *args, **kwargs):
        """
        Runs a matcher and creates the output for failed tests.
        :param var_to_test: variable being tested by the `NegatableAssertion`
        :param matcher: `NegatableAssertion` used to test the variable
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
        :param var_to_test: variable being tested by the `NegatableAssertion`
        :param matchers: Collection of `NegatableAssertion`s used to test the variable
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
        :param var_to_test: variable being tested by the `NegatableAssertion`
        :param matchers: Collection of `NegatableAssertion`s used to test the variable
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
        return negate(self.any(var_to_test, matchers, msg, *args, **kwargs))

    @contextmanager
    def raises(self, msg: Optional[str]=None, *args, **kwargs):
        failed = False
        try:
            yield
            failed = True
        except Exception as ex:
            pass
        finally:
            if failed:
                err_msg = make_message(msg or "Code failed to raise an error", *args, **kwargs)()
                raise AssertionError(err_msg)

    @contextmanager
    def raises_a(self, err_type: Type, msg: Optional[str]=None, *args, **kwargs):
        failed = False
        try:
            yield
            failed = True
        except Exception as ex:
            if not isinstance(ex, err_type):
                failed = True
        finally:
            if failed:
                err_msg = err_msg = make_message(msg or f"Code failed to raise an error of type '{err_type.__name__}'", *args, **kwargs)()
                raise AssertionError(err_msg)

    def _failure(self, var_to_test, result, msg, *args, **kwargs):
        if msg:
            err_msg = msg.format(var_to_test, *args, **kwargs)
        else:
            err_msg = result.failure_message()
        raise AssertionError(err_msg)


test_that = Tester()
