import functools
from typing import Generic, TypeVar
import schema
from schema import Schema
from inspect import isfunction
from griptape.observability.observability import Observability


CONFIG_SCHEMA = Schema({"description": str, schema.Optional("schema"): Schema})


def activity(config: dict):
    validated_config = CONFIG_SCHEMA.validate(config)

    validated_config.update({k: v for k, v in config.items() if k not in validated_config})

    if not validated_config.get("schema"):
        validated_config["schema"] = None

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        setattr(wrapper, "name", func.__name__)
        setattr(wrapper, "config", validated_config)
        setattr(wrapper, "is_activity", True)

        return wrapper

    return decorator


def observable(*args, **kwargs):
    return Observable(*args, **kwargs)


T = TypeVar("T")


class Observable(Generic[T]):
    def __init__(self, *args, **kwargs):
        self._instance = None
        if len(args) == 1 and len(kwargs) == 0 and isfunction(args[0]):
            # Parameterless call. In otherwords, the `@observable` annotation
            # was not followed by parentheses.
            self._func = args[0]
            functools.update_wrapper(self, self._func)
            self.decorator_args = ()
            self.decorator_kwargs = {}
        else:
            # Parameterized call. In otherwords, the `@observable` annotation
            # was followed by parentheses, for example `@observable()`,
            # `@observable("x")` or `@observable(y="y")`.
            self._func = None
            self.decorator_args = args
            self.decorator_kwargs = kwargs

    def __get__(self, obj, objtype=None):
        self._instance = obj
        return self

    def __call__(self, *args, **kwargs):
        if self._func:
            # Parameterless call (self._func was a set in __init__)
            if self._instance:
                args = (self._instance, *args)
            return Observability.invoke_observable(
                self._func, self._instance, args, kwargs, self.decorator_args, self.decorator_kwargs
            )
        else:
            # Parameterized call, create and return the "rea" observable decorator
            func = args[0]
            decorated_func = Observable(func)
            decorated_func.decorator_args = self.decorator_args
            decorated_func.decorator_kwargs = self.decorator_kwargs
            return decorated_func
