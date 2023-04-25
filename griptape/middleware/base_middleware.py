from abc import ABC


class BaseMiddleware(ABC):
    def process_input(self, tool_action: callable, value: any) -> any:
        return value

    def process_output(self, tool_action: callable, value: any) -> any:
        return value
