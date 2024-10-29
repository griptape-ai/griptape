import contextvars
import threading

from griptape.utils import with_contextvars

context_var = contextvars.ContextVar("context_var")


class TestContextvarsUtils:
    def test_with_contextvars(self):
        context_var.set("test")

        def function(vals: list) -> None:
            try:
                vals.append(context_var.get())
            except LookupError:
                vals.append("fallback")

        return_values = []
        thread = threading.Thread(target=with_contextvars(function), args=(return_values,))
        thread.start()
        thread.join()

        assert return_values == ["test"]

        return_values = []
        thread = threading.Thread(target=function, args=(return_values,))
        thread.start()
        thread.join()

        assert return_values == ["fallback"]
