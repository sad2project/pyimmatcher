from itertools import tee
from typing import _Final as Final, TypeVar, Sequence, Generator, Iterable

from pyimmatcher.api import NegatableAssertion, TestResult, ResultBuilder as Result, Assertion

S = TypeVar('S', contravariant=True, bound=Sequence)
E = TypeVar('E', covariant=True)


class Contains(NegatableAssertion[Sequence[E]]):
    def __init__(self, inner: E):
        self.inner: Final = inner
        self.result: Final = Result('contains {}', repr(inner))

    def test(self, actual: Sequence[E]) -> TestResult:
        if self.inner in actual:
            return self.result.pass_('', actual)
        else:
            return self.result.fail('does not contain {}', repr(self.inner))

    def __not__(self):
        return DoesNotContain(self.inner)


class DoesNotContain(Assertion[Sequence[E]]):
    def __init__(self, inner):
        self.inner: Final = inner
        self.result: Final = Result('does not contain {}', repr(inner))

    def test(self, actual: Sequence[E]) -> TestResult:
        if self.inner not in actual:
            return self.result.simple_pass()
        else:
            return self.result.fail('contains {}', repr(self.inner))


class ContainsAllInOrder(NegatableAssertion[Sequence[E]]):
    def __init__(self, first: E, *inner_seq: E):
        self.first: Final = first
        self.inner_seq: Final = (first, *inner_seq)
        self.result: Final = Result(
            'contains all of the following elements in order: {}', inner_seq)

    def test(self, actual: Sequence[E]) -> TestResult:
        if _contains_all_in_order(actual, self.first, self.inner_seq):
            return self.result.simple_pass()
        else:
            return self.result.fail('does not contain the elements in the correct order')

    def __not__(self):
        return DoesNotContainAllInOrder(self.inner_seq)


class DoesNotContainAllInOrder(Assertion[Sequence[E]]):
    def __init__(self, first: E, *inner_seq: E):
        self.first: Final = first
        self.inner_seq: Final = (first, *inner_seq)
        self.result: Final = Result(
            'does not contain all of the following elements in order: {}', inner_seq)

    def test(self, actual: Sequence[E]) -> TestResult:
        if not _contains_all_in_order(actual, self.first, self.inner_seq):
            return self.result.simple_pass()
        else:
            return self.result.fail('contains the elements in order')


def _contains_all_in_order(actual: Sequence, first, inner_seq):
    iterator = iter(actual)
    try:
        while True:
            iterator = skip_until_element(iterator, first)
            iterator, search_iter = tee(iterator, 2)
            if starts_with(search_iter, inner_seq):
                return True
            # we have to cycle it forward, or else skip_until_element() will
            # just return the current iterator
            next(iterator)
    except StopIteration:
        return False


def skip_until_element(seq: Sequence[E], el: E) -> Generator[E, None, None]:
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


def starts_with(super_seq: Iterable[E], sub_seq: Iterable[E]):
    if super_seq == iter(super_seq):
        super_seq = tuple(super_seq)

    if sub_seq == iter(sub_seq):
        sub_seq = tuple(sub_seq)

    if len(super_seq) < len(sub_seq):
        return False

    for super_el, sub_el in zip(super_seq, sub_seq):
        if super_el != sub_el:
            return False
    return True