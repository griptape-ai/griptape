import inspect
import pytest

from unittest.mock import call
import griptape.utils.decorators as decorators
import griptape.observability.observability as observability


class TestDecorators:
    @pytest.fixture
    def observable_spy(self, mocker):
        return mocker.spy(decorators, "observable")

    @pytest.fixture
    def invoke_observable_spy(self, mocker):
        return mocker.spy(observability.Observability, "invoke_observable")

    def test_observable_function_no_parenthesis(self, invoke_observable_spy):
        from griptape.utils.decorators import observable

        @observable
        def bar(*args, **kwargs):
            """bar's docstring"""
            if args:
                return args[0]

        assert bar() == None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        original_bar = bar.__wrapped__
        assert bar.__name__ == original_bar.__name__
        assert bar.__name__ == "bar"
        assert bar.__doc__ == original_bar.__doc__
        assert bar.__doc__ == "bar's docstring"

        assert invoke_observable_spy.call_count == 4
        invoke_observable_spy.assert_has_calls(
            [
                call(original_bar, None, (), {}, (), {}),
                call(original_bar, None, ("a",), {}, (), {}),
                call(original_bar, None, ("b", "2"), {}, (), {}),
                call(original_bar, None, ("c",), {"x": "y"}, (), {}),
            ]
        )

    def test_observable_function_empty_parenthesis(self, invoke_observable_spy):
        from griptape.utils.decorators import observable

        @observable()
        def bar(*args, **kwargs):
            if args:
                return args[0]

        assert bar() == None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        original_bar = bar.__wrapped__

        assert invoke_observable_spy.call_count == 4
        invoke_observable_spy.assert_has_calls(
            [
                call(original_bar, None, (), {}, (), {}),
                call(original_bar, None, ("a",), {}, (), {}),
                call(original_bar, None, ("b", "2"), {}, (), {}),
                call(original_bar, None, ("c",), {"x": "y"}, (), {}),
            ]
        )

    def test_observable_function_args(self, invoke_observable_spy):
        from griptape.utils.decorators import observable

        @observable("one", 2, {"th": "ree"}, a="b", b=6)
        def bar(*args, **kwargs):
            if args:
                return args[0]

        assert bar() == None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        original_bar = bar.__wrapped__

        assert invoke_observable_spy.call_count == 4
        invoke_observable_spy.assert_has_calls(
            [
                call(original_bar, None, (), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(original_bar, None, ("a",), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(original_bar, None, ("b", "2"), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(original_bar, None, ("c",), {"x": "y"}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
            ]
        )

    def test_observable_method_no_parenthesis(self, invoke_observable_spy):
        from griptape.utils.decorators import observable

        class Foo:
            @observable
            def bar(self, *args, **kwargs):
                if args:
                    return args[0]
                return None

        foo = Foo()
        assert foo.bar() == None
        assert foo.bar("a") == "a"
        assert foo.bar("b", "2") == "b"
        assert foo.bar("c", x="y") == "c"

        original_bar = foo.bar.__wrapped__

        assert invoke_observable_spy.call_count == 4
        invoke_observable_spy.assert_has_calls(
            [
                call(original_bar, foo, (foo,), {}, (), {}),
                call(original_bar, foo, (foo, "a"), {}, (), {}),
                call(original_bar, foo, (foo, "b", "2"), {}, (), {}),
                call(original_bar, foo, (foo, "c"), {"x": "y"}, (), {}),
            ]
        )

    def test_observable_method_empty_parenthesis(self, invoke_observable_spy):
        from griptape.utils.decorators import observable

        class Foo:
            @observable()
            def bar(self, *args, **kwargs):
                if args:
                    return args[0]
                return None

        foo = Foo()
        assert foo.bar() == None
        assert foo.bar("a") == "a"
        assert foo.bar("b", "2") == "b"
        assert foo.bar("c", x="y") == "c"

        original_bar = foo.bar.__wrapped__

        assert invoke_observable_spy.call_count == 4
        invoke_observable_spy.assert_has_calls(
            [
                call(original_bar, foo, (foo,), {}, (), {}),
                call(original_bar, foo, (foo, "a"), {}, (), {}),
                call(original_bar, foo, (foo, "b", "2"), {}, (), {}),
                call(original_bar, foo, (foo, "c"), {"x": "y"}, (), {}),
            ]
        )

    def test_observable_method_args(self, invoke_observable_spy):
        from griptape.utils.decorators import observable

        class Foo:
            @observable("one", 2, {"th": "ree"}, a="b", b=6)
            def bar(self, *args, **kwargs):
                if args:
                    return args[0]
                return None

        foo = Foo()
        assert foo.bar() == None
        assert foo.bar("a") == "a"
        assert foo.bar("b", "2") == "b"
        assert foo.bar("c", x="y") == "c"

        original_bar = foo.bar.__wrapped__

        assert invoke_observable_spy.call_count == 4
        invoke_observable_spy.assert_has_calls(
            [
                call(original_bar, foo, (foo,), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(original_bar, foo, (foo, "a"), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(original_bar, foo, (foo, "b", "2"), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(original_bar, foo, (foo, "c"), {"x": "y"}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
            ]
        )
