from pyimmatcher.api.results import TestResult
from pyimmatcher.api.helpers import ResultBuilder as Result
from pyimmatcher.api.assertions import T, Assertion

from numbers import Real as Number
from typing import _Final as Final
from math import fabs


def is_multiple_of(base: Number) -> Assertion[Number]:
    return IsMultipleOf(base)

def is_not_multiple_of(base: Number) -> Assertion[Number]:
    return IsNotMultipleOf(base)

def is_less_than(other: Type[T]) -> Assertion[T]:
    return IsLessThan(other)

def is_less_than_or_equal_to(other: Type[T]) -> Assertion[T]:
    return IsLessThanOrEqualTo(other)

def is_greater_than(other: Type[T]) -> Assertion[T]:
    return IsGreaterThan(other)

def is_greater_than_or_equal_to(other: Type[T]) -> Assertion[T]:
    return IsGreaterThanOrEqualTo(other)

def is_close_to(other: float, delta: float) -> Assertion[float]:
    return IsCloseTo(other, delta)

def is_not_close_to(other: float, delta: float) -> Assertion[float]:
    return IsNotCloseTo(other, delta)


class IsMultipleOf(Assertion[Number]):
    def __init__(self, base: Number):
        self.base: Final = base
        self.result: Final = Result('is a multiple of {}', base)

    def test(self, actual: Number) -> TestResult:
        if (actual % self.base) == 0:
            return self.result.simple_pass()
        else:
            return self.result.fail('is not a multiple of {}', self.base)

    def __not__(self):
        return IsNotMultipleOf(self.base)


class IsNotMultipleOf(Assertion[Number]):
    def __init__(self, base: Number):
        self.base: Final = base
        self.result: Final = Result('is not a multiple of {}', base)

    def test(self, actual: Number) -> TestResult:
        if (actual % self.base) != 0:
            return self.result.simple_pass()
        else:
            return self.result.fail('is a multiple of {}', self.base)


class IsLessThan(Assertion[T]):
    def __init__(self, other: T):
        self.other: Final = other
        self.result: Final = Result('is less than {}', other)

    def test(self, actual: T) -> TestResult:
        if actual < self.other:
            return self.result.pass_('is {} which is less', actual)
        else:
            return self.result.fail('is {}, which is greater or equal', actual)


class IsLessThanOrEqualTo(Assertion[T]):
    def __init__(self, other: T):
        self.other: Final = other
        self.result: Final = Result('is less than or equal to {}', other)

    def test(self, actual: T) -> TestResult:
        if actual <= self.other:
            return self.result.pass_('is {}, which is less or equal', actual)
        else:
            return self.result.fail('is {}, which is greater', actual)


class IsGreaterThan(Assertion[T]):
    def __init__(self, other: T):
        self.other: Final = other
        self.result: Final = Result('is greater than {}', other)

    def test(self, actual: T) -> TestResult:
        if actual > self.other:
            return self.result.pass_('is {}, which is greater', actual)
        else:
            return self.result.fail('is {}, which is less or equal', actual)


class IsGreaterThanOrEqualTo(Assertion[T]):
    def __init__(self, other: T):
        self.other: Final = other
        self.result: Final = Result('is greater than or equal to {}', other)

    def test(self, actual: T) -> TestResult:
        if actual >= self.other:
            return self.result.pass_('is {}, which is greater or equal', actual)
        else:
            return self.result.fail('is {}, which is less', actual)


class IsCloseTo(Assertion[float]):
    def __init__(self, other: float, delta: float=0.00000001):
        self.other: Final = other
        self.delta: Final = delta
        self.result: Final = Result('is within {delta} of {num}', delta=delta, num=other)

    def test(self, actual: float) -> TestResult:
        if fabs(actual - self.other) <= self.delta:
            return self.result.pass_('is {}, within range', actual)
        else:
            return self.result.fail('is {}, outside of range', actual)

    def __not__(self):
        return IsNotCloseTo(self.other, self.delta)


class IsNotCloseTo(Assertion[float]):
    def __init__(self, other: float, delta: float=0.00000001):
        self.other: Final = other
        self.delta: Final = delta
        self.result: Final = Result('is not within {delta} of {num}', delta=delta, num=other)

    def test(self, actual: float) -> TestResult:
        if fabs(actual - self.other) > self.delta:
            return self.result.pass_('is {}, outside of range', actual)
        else:
            return self.result.fail('is {}, within range', actual)
