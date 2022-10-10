------------------------------
PyImmatcher for Hamcrest Users
------------------------------
Introduction
============
PyImmatcher was largely created in order to address issues I had with Hamcrest. Despite that, it is still my favorite matcher library that I've used, and it has served as an inspiration for this library. The "front end" of PyImmatcher is a spiritual successor of Hamcrest, with mostly frivolous changes. It's really the "back end" that I have the biggest issues with, so that has had a pretty major overhaul.

We'll start off looking at the front end, and then we'll move on to the back.

Using PyImmatcher
==================================================
PyImmatcher is yet another matcher library for unit testing. What makes it *really* repetitive is the fact that using the front end often looks a fair bit like Hamcrest. For example::

    # Hamcrest usage
    assert_that(my_list, is_(not_(empty())))

    # PyImmatcher usage
    test_that(my_list, is_not_empty())

First off, the default name of the function to run assertions has changed from `assert_that` to `test_that`, but this is really easy to change if you prefer the old name. Simply assign `assert_that = test_that`, or create a new `Tester` (which is the type of object that `test_that` is) instance named `assert_that`.

The next obvious difference is the lack of inclusion of the `is_()` and `not_()` functions for the front API.The use of `not_()` in Hamcrest could lead to really dumb outputs, so it isn't recommended in this library. It exists, but is not the recommended way to use a negated matcher, and it only works on matchers that support negation (`NegatableAssertion`).

Not only does `not_()` cause issues with output in Hamcrest, `is_()` and `not_()` both can have annoying ramifications on the naming of matcher methods. Because the English language is a little screwy, the use of these functions ends up being really inconsistent. For example, the built-in matcher for PyHamcrest, `has_length(...)`. You would never put `is_()` in front of that. And putting `not_()` there is such a programmer thing to do, since we're all used to awkward boolean checks with a `not` or `!` in there. But the point of the matchers is to be as fluent of English as possible. So, the inverse of `has_length(...)` shouldn't be `not(has_length(...))`, but should rather be `doesn't_have_length(...)`.

Another annoying thing comes from if you're a Hamcrest user in Java. In Java, there are no `is` and `not` keywords, so the functions to call are `is()` and `not()`, with no underscores. This can lead to confusion when switching between the two. Plus, those underscores are ugly.

Lastly, the inclusion and use of `is_()` and `not_()` leads to annoying nested function calls. I had to be careful and double check the number of closing parentheses in the PyHamcrest example, but I had a really easy time writing the PyImmatcher example.

*Note:* Yes, there is the `is_not()` function, but I honestly didn't know about that until I had written most of this document. It helps with some of the arguments I'm making, but doesn't fully negate them.

So those are the obvious changes to the "front end" API in PyImmatcher compared to PyHamcrest. Now let's look at the "back end".

Extras
------

Multiple Assertions
*******************
In PyHamcrest, you have the `all_of()` and `any_of()` matchers that are used like so::

    assert_that(my_val, all_of(matches1(), matches2(), matches3()))

There is a similar feature in PyImmatcher as well whose usage works like this::

    test_that.all(my_val, matches1(), matches2(), matches3())

Again, this feature results in less function call nesting, which makes getting the closing parentheses count easier. I literally screwed up and had one too few when I initially wrote the PyHamcrest example. And, in my opinion, I think the PyHamcrest one is harder to read, but that's probably subjective.

But the next feature renders all of that moot. Instead of a call to "all", we can use a more natural language::

    test_that(my_val, matches1() & matches2() & matches3())

Obviously, this works with `|` as well.

By adding `__and__()` and `__or__()` to matchers, we're able to create a significantly more fluent syntax for multiple assertions. Plus, they can be mixed together as needed. **Note** Only do simple mixing and maybe one level of nesting at most. The output doesn't show any nesting, so it can get extremely confusing as you go deeper.

Also included alongside the `any()` and `all()` methods is the `none()` method::

    test_that.none(my_val, matches1(), matches2(), matches3())

This one passes if none of the matchers pass.

`not` Operator
**************
The `not` operator is sadly unavailable. I could have sworn there was a `__not__()` method you could implement, but there isn't. Instead, using the `not` keyword turns your matcher into a boolean and *then* inverts.

There is a basic `not_()` implementation that simply reverses 'pass' to 'fail' and prepends 'not ' to the beginning of the expectation message. I don't recommend it. All the built-in matchers have alternate names to make it more fluent and give better result messages.

Writing Matchers/Assertions
============================
While I have disagreements with some of the front end of PyHamcrest, I was willing to largely live with the same philosophy. But the reason for creating this library was to make matchers less stateful (or immutable. Hence the name; a combination of "immutable" and "matcher". It also ends up sounding a bit like "immature", which this library is and probably will remain). But since I wrote this library, why not make tweaks to the front?

First, Matchers have been renamed to Assertions. At this point, I forget the reason why I changed the name. It might have been to avoid name clashes with PyHamcrest. I don't know. And I realize that this causes the name of the library to make less sense, but I like both of these decisions anyway, so I'm sticking with them.

The Basics
----------
In order to facilitate the statelessness of a matcher, it returns a full result when run, instead of just a boolean of pass/fail. This result includes the messages of the expected and actual results as well.

With the built-in helper for creating test results (`pyimmatcher.api.ResultBuilder`) imported as `Result`, most test function bodies look a lot like this::

    result = Result("<expected result message>")
    if <passes the test>:
        return result.pass_("<passing message>")
    else:
        return result.fail("<failure message>")

Often, the first line initializing the result builder is pulled up into the constructor to declutter the testing method.

There is an additional method on the result builder called `simple_pass()` that takes no arguments and uses the expected result message as the passing message.

In addition, any of the result builder methods that takes strings can also be used like the `str.format()` method. For example::

    ...
    return result.pass_("had length {}", len(obj))
    ...

Letting the result handle the formatting call does 2 things:

1. Shortens any string formatting you would have done to not have to include the call to `str.format()`
2. These methods don't run the formatting immediately; it's done lazily. This means that the formatting is only run if the message is asked for. Since most cases should be passing cases that don't require a printout, that means that it's usually not run.

Creating a Function-based Assertion
-----------------------------------
A full result object results in there effectively being one method on Assertion (with a couple pre-implemented ones for fun stuff), which means one could easily implement Assertions from single functions. In fact, there is a decorator (`pyimmatcher.api.AsAssertion`) included that does just that. If you really wanted to, you could write a one-time assertion function as a lambda right inside your test.

Most of the built-in assertions are actually created with the `AsAssertion` decorator. For example, the `has_length` assertion::

    def has_length(n):
        result = TestResultBuilder("has a length of {}", n)
        @AsAssertion
        def test(actual):
            if len(actual) == n:
                return result.simple_pass()
            else:
                return result.fail("has a length of {}", len(actual))
        return test

Non-parameterized assertions are even easier::

    @AsAssertion
    def is_None(actual):
        result = TestResultBuilder("is None")
        if actual is None:
            return result.simple_pass()
        else:
            return result.fail("is {}", actual)

What's really cool about the non-parameterized assertions is that you instantly have an instance of them. You can use it without needing the parentheses::

    test_that(my_val, is_None)

Or, you can use the assertion with parentheses, because of the additional `__call__()` method that returns `self`. This is for those who prefer the consistency of parens over the convenience of skipping them.

Creating a Class-based Assertion
--------------------------------
So, you want to be "object-oriented" or "old-fashioned", writing class-based Assertions? This is nearly as easy as doing it with the decorator (easier, if you're not used to the nested functions).

First, subclass Assertion, putting in a generic type annotation or a specific one, depending on your needs.

For example, if you're writing an Assertion that can be used on pretty much all objects::

    from pyimmatcher.api import Assertion, T  # and some more later

    class MyGeneralAssertion(Assertion[T]):
        ...

But, if you want to work with a specific type::

    from pyimmatcher.api import Assertion
    from my_code import MyType

    class MySpecificTypeAssertion(Assertion[MyType]):
        ...

Then you give it a constructor that takes in the parametrization value(s), if any. If you want, you can prep your TestResultBuilder here, too. For the examples here on out, we'll be less abstract, and build an Assertion that checks that an `int` is less than a certain value::

    from pyimmatcher.api import Assertion, TestResult, TestResultBuilder

    class IsLessThan(Assertion[int]):
        def __init__(self, excl_max):
            self.excl_max = excl_max
            self.result = TestResultBuilder("is less than {}", excl_max)

        ...

After that, we just need to add the workhorse test function::

    ...
    def test(self, actual: int) -> TestResult:
        if actual < self.excl_max:
            return self.result.pass(str(actual))
        else:
            return self.result.fail(str(actual))

And that's it! Simple.

Obviously, since it's Python, you don't need the extra typing hints or even inheritance. I do strongly suggest using the inheritance, though; that will give you free use of `and` and `or`.

Negatable Assertions
--------------------
Most of the time, Assertions have some sort of inverse to them. For example, "is empty" has an inverse of "is not empty".

In PyHamcrest, you'd access those inverses using the `not_()` function, which simply reversed the boolean result and added the word "not" in front of their descriptions.

I disagree with this whole practice. I *did* reluctantly provide a `not_()` function to create a negated `Assertion`, but it only works with `NegatableAssertion` types (or an `Assertion` that has the `__not__()` method that returns an `Assertion` that is a negation. If you don't override the implementation of `__not__()` in `NegatableAssertion`, you'll end up with the same implementation as PyHamcrest, since it is a reasonable default implementation for some simple cases.

But the recommendation is to do a custom `Assertion` type for the negation in order to preserve the clear English language, and then you implement `__not__` to create an instance of that instead.

Here, I would also like to recommend not making the negated version of the `Assertion` negatable. Doing so would allow double negatives to exist, and, again, the recommendations with this library are to preserve clear English.

If you want to learn more about PyImmatcher, you'll need to consult the rest of the documentation.
