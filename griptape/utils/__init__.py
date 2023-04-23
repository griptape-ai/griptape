import json
from .j2 import J2
from .conversation import Conversation
from .tool_loader import ToolLoader
from .manifest_validator import ManifestValidator
from .python_runner import PythonRunner
from .command_runner import CommandRunner
from .decorators import (
    action
)

__all__ = [
    "J2",
    "Conversation",
    "ToolLoader",
    "ManifestValidator",
    "PythonRunner",
    "CommandRunner",
    "action"
]


def minify_json(value: str) -> str:
    return json.dumps(json.loads(value), separators=(',', ':'))
