from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from pyimmatcher.api import TestResult, AllOfTestResult, AnyOfTestResult, negate

T = TypeVar('T', contravariant=True)


class Assertion(ABC, Generic[T]):
    """
        The main heart of this testing library, `Assertion`s are largely the same thing as
        `Matcher`s from Hamcrest, but designed to be more pure and functional. As
        such, they only have the one check method, and the message building
        functionality is delegated to the `TestResult` returned from the `test()`
        method. To learn more about the design decisions around this, see
        `TestResult`'s documentation.
        """

    @abstractmethod
    def test(self, actual: T) -> TestResult:
        """
        Does the actual test and returns the result of that test; whether it
        passed or failed and what the expected and actual results were.
        :param actual: actual object being tested
        :return: `TestResult` that is a representative of the result of the test
        """
        pass

    def and_(self, other):
        return self.__and__(other)

    def or_(self, other):
        return self.__or__(other)

    def __and__(self, other):
        return AllOfAssertion(self, other)

    def __or__(self, other):
        return AnyOfAssertion(self, other)

    def __invert__(self):
        return SimpleNegatedAssertion(self)


def not_(assertion: Assertion[T]) -> Assertion[T]:
    return ~assertion


class AllOfAssertion(Assertion[T]):
    def __init__(self, *assertions: Assertion[T]):
        self.assertions = list(assertions)

    def test(self, actual: T) -> TestResult:
        return AllOfTestResult(
            [assertion.test(actual) for assertion in self.assertions])

    def __and__(self, other: Assertion[T]) -> Assertion[T]:
        if isinstance(other, AllOfAssertion):
            self.assertions.extend(other.assertions)
        else:
            self.assertions.append(other)
        return self

    def __or__(self, other: Assertion[T]) -> Assertion[T]:
        return AnyOfAssertion(self, other)


class AnyOfAssertion(Assertion[T]):
    def __init__(self, *assertions: Assertion[T]):
        self.assertions = list(assertions)

    def test(self, actual: T) -> TestResult:
        return AnyOfTestResult(
            [assertion.test(actual) for assertion in self.assertions])

    def __and__(self, other: Assertion[T]) -> Assertion[T]:
        return AllOfAssertion(self, other)

    def __or__(self, other: Assertion[T]):
        if isinstance(other, AnyOfAssertion):
            self.assertions.extend(other.assertions)
        else:
            self.assertions.append(other)
        return self


class SimpleNegatedAssertion(Assertion[T]):
    def __init__(self, assertion: Assertion[T]):
        self.assertion = assertion

    def test(self, actual: T) -> TestResult:
        return negate(self.assertion.test(actual))

    def __invert__(self) -> Assertion[T]:
        return self.assertion
