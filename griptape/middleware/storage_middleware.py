from __future__ import annotations
from typing import TYPE_CHECKING
from griptape.middleware import BaseMiddleware
from attr import define, field

if TYPE_CHECKING:
    from griptape.drivers import BaseStorageDriver


@define
class StorageMiddleware(BaseMiddleware):
    driver: BaseStorageDriver = field(kw_only=True)

    def process_output(self, tool_action: callable, value: bytes) -> bytes:
        from griptape.utils import J2

        return J2("middleware/storage.j2").render(
            storage_name=self.name,
            tool_name=tool_action.__self__.name,
            action_name=tool_action.config["name"],
            key=self.driver.save(value)
        ).encode()
