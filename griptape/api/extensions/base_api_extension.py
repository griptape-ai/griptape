from __future__ import annotations
from abc import ABC
from attr import define, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from griptape.api import ToolApiGenerator


@define
class BaseApiExtension(ABC):
    route_fns: list[Callable[[ToolApiGenerator], dict]] = field(factory=list, kw_only=True)

    def extend(self, generator: ToolApiGenerator) -> ToolApiGenerator:
        for route_fn in self.route_fns:
            generator.api.add_api_route(**route_fn(generator))

        return generator
