from numbers import Real as Number
from math import fabs

from pyimmatcher.api.results import TestResult, BasicResult as Result, make_message
from pyimmatcher.api.assertions import T, Assertion


class IsMultipleOf(Assertion[Number]):
    def __init__(self, base: Number):
        self.base = base

    def test(self, actual: Number) -> TestResult:
        return Result(
            (actual % self.base) == 0,
            make_message('{} is not a multiple of {}', actual, self.base),
            make_message('{} is a multiple of {}', actual, self.base))


class IsDivisibleBy(Assertion[Number]):
    def __init__(self, base: Number):
        self.base = base

    def test(self, actual: Number) -> TestResult:
        return Result(
            (actual % self.base) == 0,
            make_message('{} is not divisible by {}', actual, self.base),
            make_message('{} is divisible by {}', actual, self.base))


class IsLessThan(Assertion[T]):
    def __init__(self, bound: T):
        self.bound = bound

    def test(self, actual: T) -> TestResult:
        return Result(
            actual < self.bound,
            make_message('{} is not less than {}', actual, self.bound),
            make_message('{} is less than {}', actual, self.bound))


class IsLessThanOrEqualTo(Assertion[T]):
    def __init__(self, bound: T):
        self.bound = bound

    def test(self, actual: T) -> TestResult:
        return Result(
            actual <= self.bound,
            make_message('{} is not less than or equal to {}', actual, self.bound),
            make_message('{} is less than or equal to {}', actual, self.bound))


class IsGreaterThan(Assertion[T]):
    def __init__(self, bound: T):
        self.bound = bound

    def test(self, actual: T) -> TestResult:
        return Result(
            actual > self.bound,
            make_message('{} is not greater than {}', actual, self.bound),
            make_message('{} is greater than {}', actual, self.bound))


class IsGreaterThanOrEqualTo(Assertion[T]):
    def __init__(self, bound: T):
        self.bound = bound

    def test(self, actual: T) -> TestResult:
        return Result(
            actual >= self.bound,
            make_message('{} is not greater than or equal to {}', actual, self.bound),
            make_message('{} is greater than or equal to {}', actual, self.bound))


class IsCloseTo(Assertion[float]):
    def __init__(self, other: float, *, delta: float=0.00000001):
        self.other = other
        self.delta = delta

    def test(self, actual: float) -> TestResult:
        return Result(
            fabs(actual - self.other) <= self.delta,
            make_message('{} is not within {} ± {}', actual, self.other, self.delta),
            make_message('{} is within {} ± {}', actual, self.other, self.delta))


def is_multiple_of(base: Number) -> Assertion[Number]:
    return IsMultipleOf(base)


def is_not_multiple_of(base: Number) -> Assertion[Number]:
    return ~IsMultipleOf(base)


def is_less_than(bound: T) -> Assertion[T]:
    return IsLessThan(bound)


def is_less_than_or_equal_to(bound: T) -> Assertion[T]:
    return IsLessThanOrEqualTo(bound)


def is_greater_than(bound: T) -> Assertion[T]:
    return IsGreaterThan(bound)


def is_greater_than_or_equal_to(bound: T) -> Assertion[T]:
    return IsGreaterThanOrEqualTo(bound)


def is_close_to(other: float, *, delta: float=0.00000001) -> Assertion[float]:
    return IsCloseTo(other, delta=delta)


def is_not_close_to(other: float, *, delta: float=0.00000001) -> Assertion[float]:
    return ~IsCloseTo(other, delta=delta)
