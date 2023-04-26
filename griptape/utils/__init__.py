import json
from .paths import abs_path
from .j2 import J2
from .conversation import Conversation
from .manifest_validator import ManifestValidator
from .python_runner import PythonRunner
from .command_runner import CommandRunner


def minify_json(value: str) -> str:
    return json.dumps(json.loads(value), separators=(',', ':'))


__all__ = [
    "Conversation",
    "ManifestValidator",
    "PythonRunner",
    "CommandRunner",
    "minify_json",
    "J2",
]
