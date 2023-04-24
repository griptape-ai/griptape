from griptape.middleware import BaseMiddleware


class StorageMiddleware(BaseMiddleware):
    def process_output(self, value: any) -> any:
        return value
