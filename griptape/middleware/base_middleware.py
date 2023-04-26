from abc import ABC


class BaseMiddleware(ABC):
    def process_input(self, tool_action: callable, value: bytes) -> bytes:
        return value

    def process_output(self, tool_action: callable, value: bytes) -> bytes:
        return value
