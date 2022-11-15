from typing import Sized

from pyimmatcher.api.assertions import *
from pyimmatcher.api.results import TestResult, BasicResult as Result, make_message


class IsEqualTo(Assertion[T]):
    def __init__(self, other: T):
        self.other = other

    def test(self, actual: T) -> TestResult:
        return Result(
            actual == self.other,
            make_message('{} is not equal to {}', actual, self.other),
            make_message('{} is equal to {}', actual, self.other))


class HasLength(Assertion[Sized]):
    def __init__(self, length: int):
        self.length = length

    def test(self, actual: Sized) -> TestResult:
        return Result(
            len(actual) == self.length,
            make_message('{} does not have a length of {}', actual, self.length),
            make_message('{} has a length of {}', actual, self.length))


class HasProperty(Assertion[T]):
    def __init__(self, prop_name: str):
        self.prop_name = prop_name

    def test(self, actual: T) -> TestResult:
        return Result(
            hasattr(actual, self.prop_name),
            make_message('{} does not have property "{}"', actual, self.prop_name),
            make_message('{} has property "{}"', actual, self.prop_name))

    def with_value(self, prop_val):
        return self.that(equals(prop_val))

    def with_value_other_than(self, prop_val):
        return self.that(is_not_equal_to(prop_val))

    def that(self, assertion: Assertion):
        return HasPropertyThat(self, assertion)


class HasPropertyThat(Assertion[T]):
    def __init__(self, has_prop_assertion: HasProperty[T], val_assertion: Assertion):
        self.has_prop = has_prop_assertion
        self.val_assertion = val_assertion

    def test(self, actual: T) -> TestResult:
        has_prop_result = self.has_prop.test(actual)
        if has_prop_result.failed:
            return has_prop_result
        return self._test_value(getattr(actual, self.has_prop.prop_name))

    def _test_value(self, value):
        val_result = self.val_assertion.test(value)
        return val_result.prefaced_with(
            'for property "{prop}":\n{inner}',
            prop=self.has_prop.prop_name)

    def __invert__(self):
        return NotImplemented


class HasMethod(Assertion[T]):
    def __init__(self, method_name: str):
        self.method_name = method_name

    def test(self, actual: T) -> TestResult:
        if hasattr(actual, self.method_name):
            return self.test_is_method(getattr(actual, self.method_name))
        else:
            return Result(
                False,
                make_message('does not have method "{}"', self.method_name),
                lambda: "")  # can never use the negated message because passed = False

    def test_is_method(self, prop):
        return Result(
            callable(prop),
            make_message('"{}" exists, but is not a method', self.method_name),
            make_message('has method "{}"', self.method_name))


class HasString(Assertion[T]):
    def __init__(self, expected: str):
        self.expected = expected

    def test(self, actual: T) -> TestResult:
        actual_str = str(actual)
        return Result(
            actual_str == self.expected,
            make_message('"{}" is not the same str() form as "{}"', actual_str, self.expected),
            make_message('"{}" is the same str() form as "{}"', actual_str, self.expected))


class HasRepr(Assertion[T]):
    def __init__(self, expected: str):
        self.expected = expected

    def test(self, actual: T) -> TestResult:
        actual_repr = repr(actual)
        return Result(
            actual_repr == self.expected,
            make_message('"{}" is not the same repr() as "{}"', actual_repr, self.expected),
            make_message('"{}" is the same repr() as "{}"', actual_repr, self.expected))


class IsInstanceOf(Assertion[T]):
    message = 'is instance of {}'

    def __init__(self, expected_type: type):
        self.expected_type = expected_type

    def test(self, actual: T) -> TestResult:
        expected_type_name = self.expected_type.__qualname__
        return Result(
            isinstance(actual, self.expected_type),
            make_message('{} is not of type {}', actual, expected_type_name),
            make_message('{} is of type {}', actual, expected_type_name))


class Is(Assertion[T]):
    def __init__(self, other: T):
        self.other = other

    def test(self, actual: T) -> TestResult:
        return Result(
            actual is self.other,
            make_message('{} is not {}', actual, self.other),
            make_message('{} is {}', actual, self.other))


@AsAssertion
def IsTrue(actual):
    return Result(
        actual,
        make_message('is False'),
        make_message('is True'))


is_True = IsTrue()
is_False = ~is_True()


@AsAssertion
def IsNone(actual):
    return Result(
        actual is None,
        make_message('{} value is not None', type(actual).__name__),
        make_message('value is None'))


is_None = IsNone()
is_not_None = ~is_None()


@AsAssertion
def is_callable(actual):
    return Result(
        callable(actual),
        make_message('{} is not callable', actual),
        make_message('{} is callable', actual))


def is_not_callable():
    return ~is_callable()


def is_equal_to(other: T) -> Assertion[T]:
    return IsEqualTo(other)


def equals(other: T) -> Assertion[T]:
    return IsEqualTo(other)


def is_not_equal_to(other: T) -> Assertion[T]:
    return ~IsEqualTo(other)


def has_length(length: int) -> Assertion[T]:
    return HasLength(length)


def does_not_have_length(length: int) -> Assertion[T]:
    return ~HasLength(length)


def has_property(prop_name: str) -> HasProperty[T]:
    return HasProperty(prop_name)


def does_not_have_property(prop_name: str) -> Assertion[T]:
    return ~HasProperty(prop_name)


def has_property_with_value(prop_name: str, prop_val) -> Assertion[T]:
    return HasProperty(prop_name).with_value(prop_val)


def has_property_with_value_other_than(prop_name: str, prop_val) -> Assertion[T]:
    return HasProperty(prop_name).with_value_other_than(prop_val)


def has_method(method_name: str):
    return HasMethod(method_name)


def has_string(string: str) -> Assertion[T]:
    return HasString(string)


def does_not_have_string(string: str) -> Assertion[T]:
    return ~HasString(string)


def has_repr(string: str) -> Assertion[T]:
    return HasRepr(string)


def does_not_have_repr(string: str) -> Assertion[T]:
    return ~HasRepr(string)


def is_instance_of(clazz: type) -> Assertion[T]:
    return IsInstanceOf(clazz)


def is_a(expected_type: type) -> Assertion[T]:
    return IsInstanceOf(expected_type)


def is_not_instance_of(clazz: type) -> Assertion[T]:
    return ~IsInstanceOf(clazz)


def is_not_a(expected_type: type) -> Assertion:
    return ~IsInstanceOf(expected_type)


def is_(other: T) -> Assertion[T]:
    return Is(other)


def is_not(other: T) -> Assertion[T]:
    return ~Is(other)
