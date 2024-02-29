import functools
import schema
import inspect
import warnings

from schema import Schema


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


def deprecated(reason: str):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    Args:
        reason: The reason why the function is deprecated.
    """

    def decorator(func):
        if inspect.isclass(func):
            message = "Call to deprecated class {name} ({reason})."
        else:
            message = "Call to deprecated function {name} ({reason})."

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(message.format(name=func.__name__, reason=reason), category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter("default", DeprecationWarning)

            return func(*args, **kwargs)

        return wrapper

    return decorator
