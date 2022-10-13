from collections.abc import Collection
from itertools import tee
from typing import TypeVar, Sequence, Generator, Iterable

from pyimmatcher.api import TestResult, BasicResult as Result, Assertion, make_message, AsAssertion, \
    AllOfTestResult, AnyOfTestResult, NoneOfTestResult


S = TypeVar('S', contravariant=True, bound=Sequence)
E = TypeVar('E', covariant=True)


class Contains(Assertion[Sequence[E]]):
    def __init__(self, inner: E):
        self.inner = inner

    def test(self, actual: Sequence[E]) -> TestResult:
        return Result(
            self.inner in actual,
            make_message('{0} does not contain {1}', actual, self.inner),
            make_message('{0} contains {1}', actual, self.inner))


class ContainsAllInOrder(Assertion[Sequence[E]]):
    def __init__(self, first: E, *inner_seq: E):
        self.first = first
        self.inner_seq = (first, *inner_seq)

    def test(self, actual: Sequence[E]) -> TestResult:
        return Result(
            _contains_all_in_order(actual, self.first, self.inner_seq),
            make_message(
                '{0} does not contain, in order, {1}',
                actual,
                (self.first, *self.inner_seq)),
            make_message(
                '{0} does not contain, in order, {1}',
                actual,
                (self.first, *self.inner_seq)))


def _contains_all_in_order(actual: Sequence, first, inner_seq):
    iterator = iter(actual)
    try:
        while True:
            iterator = _skip_until_element(iterator, first)
            iterator, search_iter = tee(iterator, 2)
            if _starts_with(search_iter, inner_seq):
                return True
            # we have to cycle it forward, or else skip_until_element() will
            # just return the current iterator
            next(iterator)
    except StopIteration:
        return False


def _skip_until_element(seq: Sequence[E], el: E) -> Generator[E, None, None]:
    try:
        iterator = iter(seq)
        current = next(iterator)

        # loop through the iterator until you find an element that matches or
        # until you hit the end
        while current != el:
            current = next(iterator)

        # yield the matching element as well as the rest of the iterator
        yield current
        yield from iterator
    except StopIteration:
        return


def _starts_with(super_seq: Iterable[E], sub_seq: Iterable[E]):
    super_seq = _generate(super_seq)  # turn them into tuples if they're just iterators
    sub_seq = _generate(sub_seq)

    if len(super_seq) < len(sub_seq):
        return False

    return all(
        super_el == sub_el
        for super_el, sub_el in zip(super_seq, sub_seq))


def _generate(seq: Iterable[E]) -> Collection[E]:
    return tuple(seq) if seq == iter(seq) else seq


class AllPass(Assertion[Sequence[E]]):
    def __init__(self, assertion: Assertion[E]):
        self.assertion = assertion

    def test(self, actual: Sequence[E]) -> TestResult:
        return AllOfTestResult([self.assertion.test(item) for item in actual])


class AnyPass(Assertion[Sequence[E]]):
    def __init__(self, assertion: Assertion[E]):
        self.assertion = assertion

    def test(self, actual: Sequence[E]) -> TestResult:
        return AnyOfTestResult([self.assertion.test(item) for item in actual])


class NonePass(Assertion[Sequence[E]]):
    def __init__(self, assertion: Assertion[E]):
        self.assertion = assertion

    def test(self, actual: Sequence[E]) -> TestResult:
        return NoneOfTestResult([self.assertion.test(item) for item in actual])


class HasLength(Assertion[Sequence]):
    def __init__(self, expected_length):
        self.expected_length = expected_length

    def test(self, actual: Sequence) -> TestResult:
        actual_length = len(actual)
        return Result(
            actual_length == self.expected_length,
            make_message('length is {} instead of {}', actual_length, self.expected_length),
            make_message('length is {}', actual_length))


@AsAssertion
def IsEmpty(actual):
    return Result(
        len(actual) == 0,
        make_message('is not empty'),
        make_message('is empty'))


is_empty = IsEmpty()
is_not_empty = ~is_empty


def contains(item: E) -> Assertion[Sequence[E]]:
    return Contains(item)


def does_not_contain(item: E) -> Assertion[Sequence[E]]:
    return ~Contains(item)


def contains_all_in_order(items: Sequence[E]) -> Assertion[Sequence[E]]:
    return ContainsAllInOrder(items)


def all_items_pass(assertion: Assertion[E]) -> Assertion[Sequence[E]]:
    return AllPass(assertion)


def not_all_items_pass(assertion: Assertion[E]) -> Assertion[Sequence[E]]:
    return ~AllPass(assertion)


def any_items_pass(assertion: Assertion[E]) -> Assertion[Sequence[E]]:
    return AnyPass(assertion)


def no_items_pass(assertion: Assertion[E]) -> Assertion[Sequence[E]]:
    return NonePass(assertion)


def has_length(length: int) -> Assertion[Sequence]:
    return HasLength(length)


def does_not_have_length(length: int) -> Assertion[Sequence]:
    return ~HasLength(length)
