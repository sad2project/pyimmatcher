import re

from pyimmatcher.api import TestResult, BasicResult as Result, Assertion, AsAssertion, \
    make_message


class EndsWith(Assertion[str]):
    def __init__(self, suffix: str):
        self.suffix = suffix

    def test(self, actual: str) -> TestResult:
        return Result(
            actual.endswith(self.suffix),
            make_message('"{}" does not end with "{}"', actual, self.suffix),
            make_message('"{}" ends with "{}"', actual, self.suffix))


class StartsWith(Assertion[str]):
    def __init__(self, prefix: str):
        self.prefix = prefix

    def test(self, actual: str) -> TestResult:
        return Result(
            actual.startswith(self.prefix),
            make_message('"{}" does not start with "{}"', actual, self.prefix),
            make_message('"{}" starts with "{}"', actual, self.prefix))


class ContainsIgnoringCase(Assertion[str]):
    def __init__(self, substr: str):
        self.substr = substr

    def test(self, actual: str) -> TestResult:
        return Result(
            self.substr.lower() in actual.lower(),
            make_message('"{}" is not in "{}", ignoring case', self.substr, actual),
            make_message('"{}" is in "{}", ignoring case', self.substr, actual))


class HasNLines(Assertion[str]):
    def __init__(self, num_lines: int):
        self.num_lines = num_lines

    def test(self, actual: str) -> TestResult:
        actual_num_lines = actual.count('\n')
        return Result(
            actual_num_lines == self.num_lines,
            make_message('has {} lines instead of {}', actual_num_lines, self.num_lines),
            make_message('has {} lines', actual_num_lines))


class MatchesRegex(Assertion[str]):
    def __init__(self, regex: str):
        self.regex = regex

    def test(self, actual: str) -> TestResult:
        return Result(
            re.compile(self.regex).match(actual) is not None,
            make_message('"{}" does not match regex "{}"', actual, self.regex),
            make_message('"{}" matches regex "{}"', actual, self.regex))


class FullyMatchesRegex(Assertion[str]):
    def __init__(self, regex: str):
        self.regex = regex

    def test(self, actual: str) -> TestResult:
        return Result(
            re.compile(self.regex).fullmatch(actual) is not None,
            make_message('"{}" does not match regex "{}"', actual, self.regex),
            make_message('"{}" matches regex "{}"', actual, self.regex))


@AsAssertion
def IsEmpty(actual: str):
    return Result(
        len(str) == 0,
        make_message('"{}" is not an empty string', actual),
        make_message('is an empty string'))


@AsAssertion
def IsBlank(actual: str):
    return Result(
        len(actual.strip()) == 0,
        make_message('"{}" is not a blank string', actual),
        make_message('"{}" is a blank string', actual))


@AsAssertion
def IsLowerCase(actual: str):
    return Result(
        actual.islower(),
        make_message('"{}" is not all lower-cased', actual),
        make_message('"{}" is all lower-cased', actual))


@AsAssertion
def IsUpperCase(actual: str):
    return Result(
        actual.isupper(),
        make_message('"{}" is not all upper-cased', actual),
        make_message('"[]" is all upper-cased', actual))


def contains_ignoring_case(inner:str) -> Assertion[str]:
    return ContainsIgnoringCase(inner)


def does_not_contain_ignoring_case(inner: str) -> Assertion[str]:
    return ~ContainsIgnoringCase(inner)


def ends_with(suffix: str) -> Assertion[str]:
    return EndsWith(suffix)


def does_not_end_with(suffix: str) -> Assertion[str]:
    return ~EndsWith(suffix)


def starts_with(prefix: str) -> Assertion[str]:
    return StartsWith(prefix)


def does_not_start_with(prefix: str) -> Assertion[str]:
    return ~StartsWith(prefix)


def has_n_lines(lines: int) -> Assertion[str]:
    return HasNLines(lines)


def does_not_have_n_lines(lines: int) -> Assertion[str]:
    return ~HasNLines(lines)


def matches_regex(regex: str) -> Assertion[str]:
    return MatchesRegex(regex)


def does_not_match_regex(regex: str) -> Assertion[str]:
    return ~MatchesRegex(regex)


def fully_matches_regex(regex: str) -> Assertion[str]:
    return FullyMatchesRegex(regex)


def does_not_fully_match(regex: str) -> Assertion[str]:
    return ~FullyMatchesRegex(regex)


is_empty_str = IsEmpty()
is_not_empty_str = ~is_empty_str
is_blank_str = IsBlank()
is_not_blank_str = ~is_blank_str
is_lower_case = IsLowerCase()
is_not_lower_case = ~is_lower_case
is_upper_case = IsUpperCase()
is_not_upper_case = ~is_upper_case
