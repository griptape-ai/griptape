import os
from .base_middleware import BaseMiddleware
from .base_tool import BaseTool
from .base_executor import BaseExecutor
from .base_adapter import BaseAdapter
from .decorators import (
    action
)

PACKAGE_ABS_PATH = os.path.dirname(os.path.abspath(__file__))


def abs_path(path: str) -> str:
    return os.path.join(PACKAGE_ABS_PATH, path)


__all__ = [
    "BaseTool",
    "BaseExecutor",
    "BaseAdapter",
    "BaseMiddleware",
    "action"
]
