from itertools import tee
from typing import TypeVar, Sequence, Generator, Iterable

from pyimmatcher.api import TestResult, BasicResult as Result, Assertion, make_message, tabbed

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


class AllPass(Assertion[Sequence[E]]):
    def __init__(self, assertion: Assertion[E]):
        self.check_item = assertion

    def test(self, test_seq: Sequence[E]) -> TestResult:
        item_results = map(self.check_item.test, test_seq)
        failed_items = list(filter(lambda res: res.failed, item_results))

        return Result(
            len(failed_items) == 0,
            some_items_failed(failed_items),
            make_message('All items passed'))


def some_items_failed(failed_items):
    failure_messages = map(TestResult.failure_message, failed_items)
    return lambda: 'Some items failed:\n' + tabbed('\n'.join(failure_messages))
