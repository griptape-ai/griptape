import contextvars
import threading

from griptape.utils.decorators import with_context


class TestDecorators:
    def test_with_context_decorator(self):
        context_var = contextvars.ContextVar("context_var")
        context_var.set("test")

        @with_context
        def decorated_function(vals: list) -> None:
            vals.append(context_var.get())

        return_values = []
        thread = threading.Thread(target=decorated_function, args=(return_values,))
        thread.start()
        thread.join()

        assert return_values == ["test"]

    def test_with_context_direct(self):
        context_var = contextvars.ContextVar("context_var")
        context_var.set("test")

        def decorated_function(vals: list) -> None:
            vals.append(context_var.get())

        decorated_function = with_context(decorated_function)

        return_values = []
        thread = threading.Thread(target=decorated_function, args=(return_values,))
        thread.start()
        thread.join()

        assert return_values == ["test"]
