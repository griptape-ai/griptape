import json
from .j2 import J2
from .manifest_validator import ManifestValidator
from .python_runner import PythonRunner
from .command_runner import CommandRunner


def minify_json(value: str) -> str:
    return json.dumps(json.loads(value), separators=(',', ':'))


__all__ = [
    "J2",
    "ManifestValidator",
    "PythonRunner",
    "CommandRunner"
]
