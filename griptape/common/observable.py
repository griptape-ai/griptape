from __future__ import annotations

from typing import Any, Callable, Optional

from attrs import Factory, define, field


class Observable:
    @define
    class Call:
        func: Callable = field(kw_only=True)
        instance: Optional[Any] = field(default=None, kw_only=True)
        args: tuple[Any, ...] = field(default=Factory(tuple), kw_only=True)
        kwargs: dict[str, Any] = field(default=Factory(dict), kw_only=True)
        decorator_args: tuple[Any, ...] = field(default=Factory(tuple), kw_only=True)
        decorator_kwargs: dict[str, Any] = field(default=Factory(dict), kw_only=True)
        func_result: Any = field(default=None, kw_only=True, init=False)

        def __call__(self) -> Any:
            self.func_result = self.func(*self.args, **self.kwargs)

            return self.func_result

        @property
        def tags(self) -> Optional[list[str]]:
            return self.decorator_kwargs.get("tags")

        @property
        def attributes(self) -> Optional[dict[str, Any]]:
            create_attributes = self.decorator_kwargs.get("create_attributes")

            if create_attributes is None:
                return None
            else:
                return create_attributes(self)

        @property
        def before_call_events(self) -> list[dict[str, Any]]:
            create_before_call_events = self.decorator_kwargs.get("create_before_call_events")

            if create_before_call_events is None:
                return []
            else:
                return create_before_call_events(self)

        @property
        def after_call_events(self) -> list[dict[str, Any]]:
            create_after_call_events = self.decorator_kwargs.get("create_after_call_events")

            if create_after_call_events is None:
                return []
            else:
                return create_after_call_events(self)
