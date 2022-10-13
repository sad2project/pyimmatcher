from typing import Sequence, TypeVar, Tuple, Any

from pyimmatcher.api import Assertion, TestResult, BasicResult as Result, make_message, AllOfAssertion, AllOfTestResult, \
    AnyOfTestResult, NoneOfTestResult

K = TypeVar('K')
V = TypeVar('V')


class DictContains(Assertion[dict[K, V]]):
    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value

    def test(self, actual: dict[K, V]) -> TestResult:
        try:
            return Result(
                actual[self.key] == self.value,
                make_message('dict does not contain {} = {}', self.key, self.value),
                make_message('dict contains {} = {}', self.key, self.value))
        except KeyError:
            return Result(
                False,
                make_message('dict does not have key, {}', self.key),
                make_message('dict contains {} = {}', self.key, self.value))


class ContainsKey(Assertion[dict[K, Any]]):
    def __init__(self, key: K):
        self.key = key

    def test(self, actual: dict[K, Any]) -> TestResult:
        return Result(
            self.key in actual.keys(),
            make_message('dict does not have key, {}', self.key),
            make_message('dict has key, {}', self.key))


class ContainsValue(Assertion[dict[Any, V]]):
    def __init__(self, value: V):
        self.value = value

    def test(self, actual: dict[Any, V]) -> TestResult:
        return Result(
            self.value in actual.values(),
            make_message('dict does not have value, {}', self.value),
            make_message('dict has value, {}', self.value))


class AllValuesPass(Assertion[dict[Any, V]]):
    def __init__(self, assertion: Assertion[V]):
        self.assertion = assertion

    def test(self, actual: dict[Any, V]) -> TestResult:
        return AllOfTestResult([self.assertion.test(value) for value in actual.values()])


class AllKeysPass(Assertion[dict[K, Any]]):
    def __init__(self, assertion: Assertion[K]):
        self.assertion = assertion

    def test(self, actual: dict[K, Any]) -> TestResult:
        return AllOfTestResult([self.assertion.test(key) for key in actual.keys()])


class AnyKeysPass(Assertion[dict[K, Any]]):
    def __init__(self, assertion: Assertion[K]):
        self.assertion = assertion

    def test(self, actual: dict[K, Any]) -> TestResult:
        return AnyOfTestResult([self.assertion.test(key) for key in actual.keys()])


class AnyValuesPass(Assertion[dict[Any, V]]):
    def __init__(self, assertion: Assertion[V]):
        self.assertion = assertion

    def test(self, actual: dict[Any, V]) -> TestResult:
        return AnyOfTestResult([self.assertion.test(value) for value in actual.values()])


class NoKeysPass(Assertion[dict[K, Any]]):
    def __init__(self, assertion: Assertion[K]):
        self.assertion = assertion

    def test(self, actual: dict[K, Any]) -> TestResult:
        return NoneOfTestResult([self.assertion.test(key) for key in actual.keys()])


class NoValuesPass(Assertion[dict[Any, V]]):
    def __init__(self, assertion: Assertion[V]):
        self.assertion = assertion

    def test(self, actual: dict[Any, V]) -> TestResult:
        return NoneOfTestResult([self.assertion.test(value) for value in actual.values()])


def dict_contains(key: K, value: V) -> Assertion[dict[K, V]]:
    return DictContains(key, value)


def dict_does_not_contain(key: K, value: V) -> Assertion[dict[K, V]]:
    return ~DictContains(key, value)


def dict_contains_all(entries: Sequence[Tuple[K, V]]) -> Assertion[dict[K, V]]:
    return AllOfAssertion(*(dict_contains(k, v) for k, v in entries))


def dict_contains_none(entries: Sequence[Tuple[K, V]]) -> Assertion[dict[K, V]]:
    return AllOfAssertion(*(dict_does_not_contain(k, v) for k, v in entries))


def contains_key(key: K) -> Assertion[dict[K, Any]]:
    return ContainsKey(key)


def does_not_contain_key(key: K) -> Assertion[dict[K, Any]]:
    return ~ContainsKey(key)


def contains_value(value: V) -> Assertion[dict[Any, V]]:
    return ContainsValue(value)


def does_not_contain_value(value: V) -> Assertion[dict[Any, V]]:
    return ~ContainsValue(value)


def all_keys_pass(assertion: Assertion[K]) -> Assertion[dict[K, Any]]:
    return AllKeysPass(assertion)


def all_values_pass(assertion: Assertion[V]) -> Assertion[dict[Any, V]]:
    return AllValuesPass(assertion)


def any_keys_pass(assertion: Assertion[K]) -> Assertion[dict[K, Any]]:
    return AnyKeysPass(assertion)


def any_values_pass(assertion: Assertion[V]) -> Assertion[dict[Any, V]]:
    return AnyValuesPass(assertion)


def no_keys_pass(assertion: Assertion[K]) -> Assertion[dict[K, Any]]:
    return NoKeysPass(assertion)


def no_values_pass(assertion: Assertion[V]) -> Assertion[dict[Any, V]]:
    return NoValuesPass(assertion)
