from typing import _Final as Final

from pyimmatcher.api import NegatableAssertion, TestResult, ResultBuilder as Result, Assertion
from pyimmatcher.basic.collections import Contains, DoesNotContain


class EndsWith(NegatableAssertion[str]):
    def __init__(self, suffix: str):
        self.suffix: Final = suffix
        self.result: Final = Result('ends with "{}"', suffix)

    def test(self, actual: str) -> TestResult:
        if actual.endswith(self.suffix):
            return self.result.simple_pass()
        else:
            return self.result.fail('does not end with "{}"', self.suffix)

    def __not__(self):
        return DoesNotEndWith(self.suffix)


class DoesNotEndWith(Assertion[str]):
    def __init__(self, suffix: str):
        self.suffix: Final = suffix
        self.result: Final = Result('does not end with "{}"', suffix)

    def test(self, actual: str) -> TestResult:
        if not actual.endswith(self.suffix):
            return self.result.simple_pass()
        else:
            return self.result.fail(
                'is {actual}, which ends with "{suffix}"',
                actual=actual, suffix=self.suffix)


class StartsWith(NegatableAssertion[str]):
    def __init__(self, prefix: str):
        self.prefix: Final = prefix
        self.result: Final = Result('starts with "{}"', prefix)

    def test(self, actual: str) -> TestResult:
        if actual.startswith(self.prefix):
            return self.result.simple_pass()
        else:
            return self.result.fail('does not start with "{}"', self.prefix)

    def __not__(self):
        return DoesNotStartWith(self.prefix)


class DoesNotStartWith(Assertion[str]):
    def __init__(self, prefix: str):
        self.prefix: Final = prefix
        self.result: Final = Result('does not start with "{}"', prefix)

    def test(self, actual: str) -> TestResult:
        if not actual.startswith(self.prefix):
            return self.result.simple_pass()
        else:
            return self.result.fail('starts with "{}"', self.prefix)


def contains_string(inner: str) -> NegatableAssertion[str]:
    return Contains(inner)

def does_not_contain_string(inner: str) -> Assertion[str]:
    return DoesNotContain(inner)

def ends_with(suffix: str) -> NegatableAssertion[str]:
    return EndsWith(suffix)

def does_not_end_with(suffix: str) -> Assertion[str]:
    return DoesNotEndWith(suffix)

def starts_with(prefix: str) -> NegatableAssertion[str]:
    return StartsWith(prefix)

def does_not_start_with(prefix: str) -> Assertion[str]:
    return DoesNotStartWith(prefix)