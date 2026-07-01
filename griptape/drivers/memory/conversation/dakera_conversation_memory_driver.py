from __future__ import annotations

import json
import os
import uuid
from typing import TYPE_CHECKING, Any

from attrs import Attribute, Factory, define, field

from griptape.drivers.memory.conversation import BaseConversationMemoryDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from dakera import DakeraClient

    from griptape.memory.structure import Run


@define(kw_only=True)
class DakeraConversationMemoryDriver(BaseConversationMemoryDriver):
    """A Conversation Memory Driver for Dakera.

    Dakera is a self-hosted memory server that persists conversation state across sessions. Each
    conversation is stored under its own ``conversation_id``, which is used as the Dakera ``agent_id``
    so that a conversation's memories are isolated from every other conversation. On ``store`` the
    previous snapshot is replaced with the latest one, mirroring the semantics of the other
    Conversation Memory Drivers.

    Attributes:
        base_url: The base URL of the Dakera server. Defaults to the value of the environment
            variable ``DAKERA_BASE_URL`` or ``http://localhost:3000``.
        api_key: The API key used to authenticate with the Dakera server. Defaults to the value of
            the environment variable ``DAKERA_API_KEY``. May be ``None`` for a server that does not
            require authentication.
        conversation_id: The id of the conversation. Used as the Dakera ``agent_id``.
    """

    base_url: str = field(
        default=Factory(lambda: os.getenv("DAKERA_BASE_URL", "http://localhost:3000")),
        metadata={"serializable": True},
    )
    api_key: str | None = field(
        default=Factory(lambda: os.getenv("DAKERA_API_KEY")),
        metadata={"serializable": False},
    )
    conversation_id: str = field(
        default=Factory(lambda: uuid.uuid4().hex),
        metadata={"serializable": True},
    )
    client: DakeraClient = field(
        default=Factory(
            lambda self: import_optional_dependency("dakera").DakeraClient(
                base_url=self.base_url,
                api_key=self.api_key,
            ),
            takes_self=True,
        ),
        metadata={"serializable": False},
    )

    @conversation_id.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_conversation_id(self, _: Attribute, value: str) -> str:
        if not value:
            raise ValueError(f"{self.__class__.__name__} requires a non-empty conversation_id")
        return value

    def store(self, runs: list[Run], metadata: dict[str, Any]) -> None:
        content = json.dumps(self._to_params_dict(runs, metadata))

        # Replace the previous snapshot so that load() only ever returns the latest conversation state.
        for memory in self.client.agent_memories(agent_id=self.conversation_id):
            memory_id = memory.get("id")
            if memory_id is not None:
                self.client.forget(agent_id=self.conversation_id, memory_id=memory_id)

        self.client.store_memory(
            agent_id=self.conversation_id,
            content=content,
            memory_type="episodic",
            importance=1.0,
        )

    def load(self) -> tuple[list[Run], dict[str, Any]]:
        memories = self.client.agent_memories(agent_id=self.conversation_id, limit=1)
        if memories:
            return self._from_params_dict(json.loads(memories[0]["content"]))
        return [], {}
