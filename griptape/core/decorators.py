import functools
from schema import Schema


def activity(config: dict):
    __config_schema().validate(config)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        wrapper.config = config
        wrapper.is_activity = True

        return wrapper
    return decorator


def __config_schema() -> Schema:
    return Schema({
        "name": str,
        "description": str,
        "schema": Schema
    }, ignore_extra_keys=True)
