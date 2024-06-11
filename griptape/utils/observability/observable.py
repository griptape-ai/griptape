import wrapt
from inspect import isfunction


def observable(*args, **kwargs):
    wrapped = args[0] if len(args) == 1 and len(kwargs) == 0 and isfunction(args[0]) else None
    if wrapped is not None:
        # The decorator was not called. In otherwords, the
        # `@observable` annotation was not followed by parentheses.
        return create_observable_wrapper()(wrapped)  # pyright: ignore

    # The decorator was "called", possibly with arguments. In otherwords,
    # the `@observable` annotation was followed by parentheses, for example
    # `@observable()`, `@observable("x")` or `@observable(y="y")`.
    return create_observable_wrapper(*args, **kwargs)


def create_observable_wrapper(*observable_args, **observable_kwargs):
    @wrapt.decorator
    def observable_wrapper(wrapped, instance, args, kwargs):
        wrapt_params = (wrapped, instance, args, kwargs)
        observable_params = (observable_args, observable_kwargs)
        return observable_wrapper_impl(wrapt_params, observable_params)

    return observable_wrapper


# By default observable_wrapper_impl does nothing but invoke the
# original function. If you decided to monkey patch this method to
# change the behavior, the function is provided both the wrapt
# function parameters (required to invoke the original function)
# and the parameters that were passed to the original observable
# decorator.
#
# This function can be monkey patched at runtime before or after
# the observable decorator has been applied to the target functions.
def observable_wrapper_impl(wrapt_params, observable_params):
    wrapped, instance, args, kwargs = wrapt_params
    return wrapped(*args, **kwargs)
