from griptape.core import BaseMiddleware


class StorageMiddleware(BaseMiddleware):
    def process_output(self, value: any) -> any:
        return value
