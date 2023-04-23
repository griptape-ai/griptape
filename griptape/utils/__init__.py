import json
from griptape.utils.j2 import J2
from griptape.utils.conversation import Conversation
from griptape.utils.tool_loader import ToolLoader

__all__ = [
    "J2",
    "Conversation",
    "ToolLoader"
]


def minify_json(value: str) -> str:
    return json.dumps(json.loads(value), separators=(',', ':'))
