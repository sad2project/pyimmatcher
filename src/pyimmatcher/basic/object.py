from typing import Sized

from pyimmatcher.api.assertions import *
from pyimmatcher.api.helpers import *
Result = ResultBuilder


def is_equal_to(other: Type[T]) -> Assertion[T]:
    return IsEqualTo(other)


def is_not_equal_to(other: Type[T]) -> Assertion[T]:
    return IsNotEqualTo(other)


def has_length(length: int) -> Assertion[T]:
    return HasLength(length)


def does_not_have_length(length: int) -> Assertion[T]:
    return DoesNotHaveLength(length)


def has_property(prop_name: str) -> Assertion[T]:
    return HasProperty(prop_name)


def does_not_have_property(prop_name: str) -> Assertion[T]:
    return DoesNotHaveProperty(prop_name)


def has_property_with_value(prop_name: str, prop_val) -> Assertion[T]:
    return HasPropertyWithValue(prop_name, prop_val)


def has_property_with_value_other_than(prop_name: str, prop_val) -> Assertion[T]:
    return HasPropertyWithValueOtherThan(prop_name, prop_val)


def has_string(string: str) -> Assertion[T]:
    return HasString(string)


def does_not_have_string(string: str) -> Assertion[T]:
    return DoesNotHaveString(string)


def is_instance_of(clazz: type) -> Assertion[T]:
    return IsInstanceOf(clazz)


def is_not_instance_of(clazz: type) -> Assertion[T]:
    return IsNotInstanceOf(clazz)


def is_(other: Type[T]) -> Assertion[T]:
    return Is(other)


def is_not(other: Type[T]) -> Assertion[T]:
    return IsNot(other)


class IsEqualTo(Assertion[T]):
    def __init__(self, other: Type[T]):
        self.other = other
        self.result = Result('is equal to {}', other)

    def test(self, actual: Type[T]) -> TestResult:
        if actual == self.other:
            return self.result.simple_pass()
        else:
            return self.result.fail('is {}', actual)

    def __not__(self):
        return IsNotEqualTo(self.other)


class IsNotEqualTo(Assertion[T]):
    def __init__(self, other: Type[T]):
        self.other = other
        self.result = Result('is not equal to {}', other)

    def test(self, actual: Type[T]) -> TestResult:
        if actual != self.other:
            return self.result.pass_('is {}', actual)
        else:
            return self.result.fail('is equal to {}', self.other)


class HasLength(Assertion[Sized]):
    message = 'has length of {}'

    def __init__(self, length: int):
        self.length = length
        self.result = Result(self.message, length)

    def test(self, actual: Sized) -> TestResult:
        actual_len = len(actual)
        if actual_len == self.length:
            return self.result.simple_pass()
        else:
            return self.result.fail(self.message, actual_len)

    def __not__(self):
        return DoesNotHaveLength(self.length)


class DoesNotHaveLength(Assertion[Sized]):
    def __init__(self, length: int):
        self.length = length
        self.result = Result('does not have length of {}', length)

    def test(self, actual: Sized) -> TestResult:
        actual_length = len(actual)
        if actual_length != self.length:
            return self.result.pass_('has length of {}', actual_length)
        else:
            return self.result.fail('has length of {}', actual_length)


class HasProperty(Assertion[T]):
    def __init__(self, prop_name: str):
        self.prop_name = prop_name
        self.result = Result('has property "{}"', prop_name)

    def test(self, actual: Type[T]) -> TestResult:
        if hasattr(actual, self.prop_name):
            return self.result.simple_pass()
        else:
            return self.result.fail('does not have property "{}"', self.prop_name)

    def __not__(self):
        return DoesNotHaveProperty(self.prop_name)


class DoesNotHaveProperty(Assertion[T]):
    def __init__(self, prop_name: str):
        self.prop_name = prop_name
        self.result = Result('does not have property "{}"', prop_name)

    def test(self, actual: Type[T]) -> TestResult:
        if not hasattr(actual, self.prop_name):
            return self.result.simple_pass()
        else:
            return self.result.fail('has property "{}"', self.prop_name)


class HasPropertyWithValue(Assertion[T]):
    def __init__(self, prop_name: str, prop_value):
        self.prop_name = prop_name
        self.prop_value = prop_value
        self.result = Result(
            'has property "{prop}" with value, {val}',
            prop=prop_name, val=prop_value)

    def test(self, actual: Type[T]) -> TestResult:
        if hasattr(actual, self.prop_name):
            return self._test_property_value(actual)
        else:
            return self.result.fail(
                'does not have property "{}"', self.prop_name)

    def _test_property_value(self, actual) -> TestResult:
        if getattr(actual, self.prop_name) == self.prop_value:
            return self.result.simple_pass()
        else:
            return self.result.fail(
                'has property "{prop}", but with value, {val}',
                prop=self.prop_name, val=getattr(actual, self.prop_name))


class HasPropertyWithValueOtherThan(Assertion[T]):
    def __init__(self, prop_name: str, prop_value):
        self.prop_name = prop_name
        self.prop_value = prop_value
        self.result = Result(
            'has property "{prop}" with value other than {val}',
            prop=prop_name, val=prop_value)

    def test(self, actual: Type[T]) -> TestResult:
        if hasattr(actual, self.prop_name):
            return self.test_value(getattr(actual, self.prop_name))
        else:
            return self.result.fail('does not have property "{}"', self.prop_name)

    def test_value(self, actual_value):
        if actual_value != self.prop_value:
            return self.result.fail(
                'property "{prop}" has value of {val}',
                prop=self.prop_name, val=actual_value)
        else:
            return self.result.pass_(
                'property "{prop}" has value of {val}',
                prop=self.prop_name, val=actual_value)


class HasString(Assertion[T]):
    message = 'has string form of "{}"'

    def __init__(self, string: str):
        self.string = string
        self.result = Result(self.message, string)

    def test(self, actual: Type[T]) -> TestResult:
        actual_string = str(actual)
        if actual_string == self.string:
            return self.result.simple_pass()
        else:
            return self.result.fail(self.message, actual_string)

    def __not__(self):
        return DoesNotHaveString(self.string)


class DoesNotHaveString(Assertion[T]):
    def __init__(self, string: str):
        self.string = string
        self.result = Result('does not have string form of "{}"', string)

    def test(self, actual: Type[T]) -> TestResult:
        actual_string = str(actual)
        if actual_string != self.string:
            return self.result.pass_('has string form of "{}"', actual_string)
        else:
            return self.result.fail('has string form of "{}"', actual_string)


class IsInstanceOf(Assertion[T]):
    message = 'is instance of {}'

    def __init__(self, clazz: type):
        self.clazz = clazz
        self.result = Result(self.message, clazz.__qualname__)

    def test(self, actual: Type[T]) -> TestResult:
        if isinstance(actual, self.clazz):
            return self.result.simple_pass()
        else:
            return self.result.fail(self.message, type(actual).__qualname__)

    def __not__(self):
        return IsNotInstanceOf(self.clazz)


class IsNotInstanceOf(Assertion[T]):
    def __init__(self, clazz: type):
        self.clazz = clazz
        self.result = Result('is not instance of {}', clazz.__qualname__)

    def test(self, actual: Type[T]) -> TestResult:
        if isinstance(actual, self.clazz):
            return self.test_specifics(actual)
        else:
            return self.result.pass_('is instance of {}', type(actual).__qualname__)

    def test_specifics(self, actual):
        actual_type = type(actual)
        if actual_type == self.clazz:
            return self.result.fail('is instance of {}', self.clazz.__qualname__)
        else:
            return self.result.fail(
                'is instance of {sub}, a subclass of {type}',
                sub=actual_type.__qualname__, type=self.clazz.__qualname__)


class Is(Assertion[T]):
    message = 'is {}'

    def __init__(self, other: Type[T]):
        self.other = other
        self.result = Result(self.message, other)

    def test(self, actual: Type[T]) -> TestResult:
        if actual is self.other:
            return self.result.simple_pass()
        else:
            return self.result.fail(self.message, actual)

    def __not__(self):
        return IsNot(self.other)


class IsNot(Assertion[T]):
    def __init__(self, other: Type[T]):
        self.other = other
        self.result = Result("is not {}", other)

    def test(self, actual: Type[T]) -> TestResult:
        if actual is not self.other:
            return self.result.pass_("is {}", actual)
        else:
            return self.result.fail("is {}", actual)


@AsAssertion
def is_None(actual):
    result = Result('is None')
    if actual is None:
        return result.simple_pass()
    else:
        return result.fail('is {}', actual)


@AsAssertion
def is_not_None(actual):
    result = Result('is not None')
    if actual is not None:
        return result.pass_('is {}', actual)
    else:
        return result.fail('is None')