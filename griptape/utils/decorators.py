from __future__ import annotations

import functools
from typing import Any, Callable, Optional

import schema
from schema import Schema

CONFIG_SCHEMA = Schema(
    {
        "description": str,
        schema.Optional("schema"): lambda data: isinstance(data, (Schema, Callable)),
    }
)


def activity(config: dict) -> Any:
    validated_config = CONFIG_SCHEMA.validate(config)

    validated_config.update({k: v for k, v in config.items() if k not in validated_config})

    if not validated_config.get("schema"):
        validated_config["schema"] = None

    def decorator(func: Callable) -> Any:
        @functools.wraps(func)
        def wrapper(self: Any, *args, **kwargs) -> Any:
            return func(self, *args, **kwargs)

        setattr(wrapper, "name", func.__name__)
        setattr(wrapper, "config", validated_config)
        setattr(wrapper, "is_activity", True)

        return wrapper

    return decorator


def lazy_property(attr_name: Optional[str] = None) -> Callable[[Callable[[Any], Any]], property]:
    def decorator(func: Callable[[Any], Any]) -> property:
        actual_attr_name = f"_{func.__name__}" if attr_name is None else attr_name

        @property
        @functools.wraps(func)
        def lazy_attr(self: Any) -> Any:
            if getattr(self, actual_attr_name) is None:
                setattr(self, actual_attr_name, func(self))
            return getattr(self, actual_attr_name)

        @lazy_attr.setter
        def lazy_attr(self: Any, value: Any) -> None:
            setattr(self, actual_attr_name, value)

        return lazy_attr

    return decorator
