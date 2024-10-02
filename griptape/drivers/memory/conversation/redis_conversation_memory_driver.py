from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.drivers import BaseConversationMemoryDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from redis import Redis

    from griptape.memory.structure import Run


@define
class RedisConversationMemoryDriver(BaseConversationMemoryDriver):
    """A Conversation Memory Driver for Redis.

    This driver interfaces with a Redis instance and utilizes the Redis hashes and RediSearch module to store,
    retrieve, and query conversations in a structured manner.
    Proper setup of the Redis instance and RediSearch is necessary for the driver to function correctly.

    Attributes:
        host: The host of the Redis instance.
        port: The port of the Redis instance.
        db: The database of the Redis instance.
        password: The password of the Redis instance.
        index: The name of the index to use.
        conversation_id: The id of the conversation.
    """

    host: str = field(kw_only=True, metadata={"serializable": True})
    port: int = field(kw_only=True, metadata={"serializable": True})
    db: int = field(kw_only=True, default=0, metadata={"serializable": True})
    password: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    index: str = field(kw_only=True, metadata={"serializable": True})
    conversation_id: str = field(kw_only=True, default=uuid.uuid4().hex)

    client: Redis = field(
        default=Factory(
            lambda self: import_optional_dependency("redis").Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=False,
            ),
            takes_self=True,
        ),
    )

    def store(self, runs: list[Run], metadata: dict[str, Any]) -> None:
        self.client.hset(self.index, self.conversation_id, json.dumps(self._to_params_dict(runs, metadata)))

    def load(self) -> tuple[list[Run], dict[str, Any]]:
        memory_json = self.client.hget(self.index, self.conversation_id)
        if memory_json is not None:
            return self._from_params_dict(json.loads(memory_json))  # pyright: ignore[reportArgumentType] https://github.com/redis/redis-py/issues/2399
        return [], {}
