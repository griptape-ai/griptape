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

        def __call__(self) -> Any:
            return self.func(*self.args, **self.kwargs)

        @property
        def tags(self) -> Optional[list[str]]:
            return self.decorator_kwargs.get("tags")
