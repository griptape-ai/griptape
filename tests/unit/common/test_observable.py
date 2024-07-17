from unittest.mock import call

import pytest

import griptape.observability.observability as observability
from griptape.common.observable import Observable


class TestObservable:
    @pytest.fixture()
    def observe_spy(self, mocker):
        return mocker.spy(observability.Observability, "observe")

    def test_observable_function_no_parenthesis(self, observe_spy):
        from griptape.common import observable

        @observable
        def bar(*args, **kwargs):
            """Bar's docstring."""
            if args:
                return args[0]

        assert bar() is None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        original_bar = bar.__wrapped__
        assert bar.__name__ == original_bar.__name__
        assert bar.__name__ == "bar"
        assert bar.__doc__ == original_bar.__doc__
        assert bar.__doc__ == "Bar's docstring."

        assert observe_spy.call_count == 4
        observe_spy.assert_has_calls(
            [
                call(Observable.Call(func=original_bar, args=())),
                call(Observable.Call(func=original_bar, args=("a",))),
                call(Observable.Call(func=original_bar, args=("b", "2"))),
                call(Observable.Call(func=original_bar, args=("c",), kwargs={"x": "y"})),
            ]
        )

    def test_observable_function_empty_parenthesis(self, observe_spy):
        from griptape.common import observable

        @observable()
        def bar(*args, **kwargs):
            if args:
                return args[0]

        assert bar() is None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        original_bar = bar.__wrapped__

        assert observe_spy.call_count == 4
        observe_spy.assert_has_calls(
            [
                call(Observable.Call(func=original_bar, args=())),
                call(Observable.Call(func=original_bar, args=("a",))),
                call(Observable.Call(func=original_bar, args=("b", "2"))),
                call(Observable.Call(func=original_bar, args=("c",), kwargs={"x": "y"})),
            ]
        )

    def test_observable_function_args(self, observe_spy):
        from griptape.common import observable

        @observable("one", 2, {"th": "ree"}, a="b", b=6)
        def bar(*args, **kwargs):
            if args:
                return args[0]

        assert bar() is None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        original_bar = bar.__wrapped__

        assert observe_spy.call_count == 4
        observe_spy.assert_has_calls(
            [
                call(
                    Observable.Call(
                        func=original_bar,
                        args=(),
                        decorator_args=("one", 2, {"th": "ree"}),
                        decorator_kwargs={"a": "b", "b": 6},
                    )
                ),
                call(
                    Observable.Call(
                        func=original_bar,
                        args=("a",),
                        decorator_args=("one", 2, {"th": "ree"}),
                        decorator_kwargs={"a": "b", "b": 6},
                    )
                ),
                call(
                    Observable.Call(
                        func=original_bar,
                        args=("b", "2"),
                        decorator_args=("one", 2, {"th": "ree"}),
                        decorator_kwargs={"a": "b", "b": 6},
                    )
                ),
                call(
                    Observable.Call(
                        func=original_bar,
                        args=("c",),
                        kwargs={"x": "y"},
                        decorator_args=("one", 2, {"th": "ree"}),
                        decorator_kwargs={"a": "b", "b": 6},
                    )
                ),
            ]
        )

    def test_observable_method_no_parenthesis(self, observe_spy):
        from griptape.common import observable

        class Foo:
            @observable
            def bar(self, *args, **kwargs):
                if args:
                    return args[0]
                return None

        foo = Foo()
        assert foo.bar() is None
        assert foo.bar("a") == "a"
        assert foo.bar("b", "2") == "b"
        assert foo.bar("c", x="y") == "c"

        original_bar = foo.bar.__wrapped__

        assert observe_spy.call_count == 4
        observe_spy.assert_has_calls(
            [
                call(Observable.Call(func=original_bar, instance=foo, args=())),
                call(Observable.Call(func=original_bar, instance=foo, args=("a",))),
                call(Observable.Call(func=original_bar, instance=foo, args=("b", "2"))),
                call(Observable.Call(func=original_bar, instance=foo, args=("c",), kwargs={"x": "y"})),
            ]
        )

    def test_observable_method_empty_parenthesis(self, observe_spy):
        from griptape.common import observable

        class Foo:
            @observable()
            def bar(self, *args, **kwargs):
                if args:
                    return args[0]
                return None

        foo = Foo()
        assert foo.bar() is None
        assert foo.bar("a") == "a"
        assert foo.bar("b", "2") == "b"
        assert foo.bar("c", x="y") == "c"

        original_bar = foo.bar.__wrapped__

        assert observe_spy.call_count == 4
        observe_spy.assert_has_calls(
            [
                call(Observable.Call(func=original_bar, instance=foo, args=())),
                call(Observable.Call(func=original_bar, instance=foo, args=("a",))),
                call(Observable.Call(func=original_bar, instance=foo, args=("b", "2"))),
                call(Observable.Call(func=original_bar, instance=foo, args=("c",), kwargs={"x": "y"})),
            ]
        )

    def test_observable_method_args(self, observe_spy):
        from griptape.common import observable

        class Foo:
            @observable("one", 2, {"th": "ree"}, a="b", b=6)
            def bar(self, *args, **kwargs):
                if args:
                    return args[0]
                return None

        foo = Foo()
        assert foo.bar() is None
        assert foo.bar("a") == "a"
        assert foo.bar("b", "2") == "b"
        assert foo.bar("c", x="y") == "c"

        original_bar = foo.bar.__wrapped__

        assert observe_spy.call_count == 4
        observe_spy.assert_has_calls(
            [
                call(
                    Observable.Call(
                        func=original_bar,
                        instance=foo,
                        args=(),
                        decorator_args=("one", 2, {"th": "ree"}),
                        decorator_kwargs={"a": "b", "b": 6},
                    )
                ),
                call(
                    Observable.Call(
                        func=original_bar,
                        instance=foo,
                        args=("a",),
                        decorator_args=("one", 2, {"th": "ree"}),
                        decorator_kwargs={"a": "b", "b": 6},
                    )
                ),
                call(
                    Observable.Call(
                        func=original_bar,
                        instance=foo,
                        args=("b", "2"),
                        decorator_args=("one", 2, {"th": "ree"}),
                        decorator_kwargs={"a": "b", "b": 6},
                    )
                ),
                call(
                    Observable.Call(
                        func=original_bar,
                        instance=foo,
                        args=("c",),
                        kwargs={"x": "y"},
                        decorator_args=("one", 2, {"th": "ree"}),
                        decorator_kwargs={"a": "b", "b": 6},
                    )
                ),
            ]
        )
