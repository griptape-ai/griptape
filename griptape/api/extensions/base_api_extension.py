from abc import ABC
from dataclasses import dataclass
from typing import Callable
from attr import define, field

from griptape.tools import BaseTool


@define
class BaseApiExtension(ABC):
    @dataclass
    class Route:
        path: str
        endpoint: Callable
        methods: list[str]
        description: str

    tool: BaseTool = field(kw_only=True)
    path_prefix: str = field(default="/", kw_only=True)
    routes: list[Route] = field(factory=list, kw_only=True)
