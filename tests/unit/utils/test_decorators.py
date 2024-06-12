from unittest.mock import MagicMock, call

from griptape.utils.observability.griptape_instrumentor import unwrap_function_wrapper


class TestDecorators:
    def test_observable_no_parenthesis(self, mocker):
        import griptape.utils.decorators as decorators

        observable_spy = mocker.spy(decorators, "observable")
        create_observable_wrapper_spy = mocker.spy(decorators, "create_observable_wrapper")
        observable_wrapper_impl_spy = mocker.spy(decorators, "observable_wrapper_impl")
        from griptape.utils.decorators import observable

        @observable
        def bar(*args, **kwargs):
            if args:
                return args[0]

        assert bar() == None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        assert observable_spy.call_count == 1
        observable_spy.assert_called_with(bar)
        assert create_observable_wrapper_spy.call_count == 1
        create_observable_wrapper_spy.assert_called_with()
        assert observable_wrapper_impl_spy.call_count == 4
        observable_wrapper_impl_spy.assert_has_calls(
            [
                call((bar, None, (), {}), ((), {})),
                call((bar, None, ("a",), {}), ((), {})),
                call((bar, None, ("b", "2"), {}), ((), {})),
                call((bar, None, ("c",), {"x": "y"}), ((), {})),
            ]
        )

    def test_observable_empty_parenthesis(self, mocker):
        import griptape.utils.decorators as decorators

        observable_spy = mocker.spy(decorators, "observable")
        create_observable_wrapper_spy = mocker.spy(decorators, "create_observable_wrapper")
        observable_wrapper_impl_spy = mocker.spy(decorators, "observable_wrapper_impl")
        from griptape.utils.decorators import observable

        @observable()
        def bar(*args, **kwargs):
            if args:
                return args[0]

        assert bar() == None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        assert observable_spy.call_count == 1
        observable_spy.assert_called_with()
        assert create_observable_wrapper_spy.call_count == 1
        create_observable_wrapper_spy.assert_called_with()
        assert observable_wrapper_impl_spy.call_count == 4
        observable_wrapper_impl_spy.assert_has_calls(
            [
                call((bar, None, (), {}), ((), {})),
                call((bar, None, ("a",), {}), ((), {})),
                call((bar, None, ("b", "2"), {}), ((), {})),
                call((bar, None, ("c",), {"x": "y"}), ((), {})),
            ]
        )

    def test_observable_args(self, mocker):
        import griptape.utils.decorators as decorators

        observable_spy = mocker.spy(decorators, "observable")
        create_observable_wrapper_spy = mocker.spy(decorators, "create_observable_wrapper")
        observable_wrapper_impl_spy = mocker.spy(decorators, "observable_wrapper_impl")
        from griptape.utils.decorators import observable

        @observable("one", 2, {"th": "ree"}, a="b", b=6)
        def bar(*args, **kwargs):
            if args:
                return args[0]

        assert bar() == None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        assert observable_spy.call_count == 1
        observable_spy.assert_called_with("one", 2, {"th": "ree"}, a="b", b=6)
        assert create_observable_wrapper_spy.call_count == 1
        create_observable_wrapper_spy.assert_called_with("one", 2, {"th": "ree"}, a="b", b=6)
        assert observable_wrapper_impl_spy.call_count == 4
        observable_wrapper_impl_spy.assert_has_calls(
            [
                call((bar, None, (), {}), (("one", 2, {"th": "ree"}), {"a": "b", "b": 6})),
                call((bar, None, ("a",), {}), (("one", 2, {"th": "ree"}), {"a": "b", "b": 6})),
                call((bar, None, ("b", "2"), {}), (("one", 2, {"th": "ree"}), {"a": "b", "b": 6})),
                call((bar, None, ("c",), {"x": "y"}), (("one", 2, {"th": "ree"}), {"a": "b", "b": 6})),
            ]
        )

    def test_observable_wrapt_impl(self):
        from griptape.utils.decorators import observable

        @observable("one", 2, {"th": "ree"}, a="b", b=6)
        def bar(*args, **kwargs):
            if args:
                return args[0]

        import wrapt

        mock = MagicMock()

        def observable_wrapper_impl(wrapped, instance, args, kwargs, observable_args, observable_kwargs):
            mock.impl(wrapped, instance, args, kwargs, observable_args, observable_kwargs)
            return wrapped(*args, **kwargs)

        def observable_wrapper_impl_patch(wrapped, instance, args, kwargs):
            return observable_wrapper_impl(*args[0], *args[1])

        wrapt.wrap_function_wrapper(
            "griptape.utils.decorators", "observable_wrapper_impl", observable_wrapper_impl_patch
        )

        assert bar() == None
        assert bar("a") == "a"
        assert bar("b", "2") == "b"
        assert bar("c", x="y") == "c"

        mock.impl.call_count == 4
        mock.impl.assert_has_calls(
            [
                call(bar, None, (), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(bar, None, ("a",), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(bar, None, ("b", "2"), {}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
                call(bar, None, ("c",), {"x": "y"}, ("one", 2, {"th": "ree"}), {"a": "b", "b": 6}),
            ]
        )

        unwrap_function_wrapper("griptape.utils.decorators", "observable_wrapper_impl")
