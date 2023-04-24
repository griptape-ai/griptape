from abc import ABC


class BaseMiddleware(ABC):
    def process_input(self, value: any) -> any:
        return value

    def process_output(self, value: any) -> any:
        return value