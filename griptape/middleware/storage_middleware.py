from __future__ import annotations
from typing import TYPE_CHECKING
from griptape.middleware import BaseMiddleware
from attr import define, field

if TYPE_CHECKING:
    from griptape.drivers import BaseStorageDriver


@define
class StorageMiddleware(BaseMiddleware):
    driver: BaseStorageDriver = field(kw_only=True)

    def process_output(self, tool_action: callable, value: any) -> any:
        return value
