from __future__ import annotations
from abc import ABC
from attr import define, field
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from griptape.api import ApiGenerator


@define
class BaseApiExtension(ABC):
    route_fns: list[Callable[[ApiGenerator], dict]] = field(factory=list, kw_only=True)

    def extend(self, generator: ApiGenerator) -> ApiGenerator:
        for route_fn in self.route_fns:
            generator.api.add_api_route(**route_fn(generator))

        return generator
