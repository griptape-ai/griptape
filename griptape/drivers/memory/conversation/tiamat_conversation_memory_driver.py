"""TIAMAT Cloud Memory Driver for Griptape.

Provides persistent, cloud-based conversation memory via https://memory.tiamat.live.
No infrastructure required — just an API key.

Usage::

    from griptape.drivers.memory.conversation import TiamatConversationMemoryDriver
    from griptape.memory.structure import ConversationMemory
    from griptape.structures import Agent

    driver = TiamatConversationMemoryDriver(api_key="your-key")
    memory = ConversationMemory(driver=driver)
    agent = Agent(conversation_memory=memory)
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any

import httpx

from griptape.drivers.memory.conversation.base_conversation_memory_driver import (
    BaseConversationMemoryDriver,
)

if TYPE_CHECKING:
    from griptape.memory.structure import Run


TIAMAT_BASE_URL = "https://memory.tiamat.live"


class TiamatConversationMemoryDriver(BaseConversationMemoryDriver):
    """Cloud conversation memory driver backed by TIAMAT's Memory API.

    Stores conversation runs as persistent memories in TIAMAT's cloud,
    with FTS5 full-text search and knowledge triple support.

    Attributes:
        api_key: TIAMAT API key. Falls back to TIAMAT_API_KEY env var.
        base_url: Base URL for the TIAMAT Memory API.
        agent_id: Identifier for this agent (used as storage tag).
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = TIAMAT_BASE_URL,
        agent_id: str = "griptape-agent",
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get("TIAMAT_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.agent_id = agent_id
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def store(self, runs: list[Run], metadata: dict[str, Any]) -> None:
        """Store conversation runs in TIAMAT's cloud memory.

        Args:
            runs: List of conversation Run objects.
            metadata: Additional metadata dict.
        """
        params_dict = self._to_params_dict(runs, metadata)

        try:
            self._client.post(
                "/api/memory/store",
                json={
                    "content": json.dumps(params_dict, ensure_ascii=False),
                    "tags": [
                        f"agent:{self.agent_id}",
                        "conversation_memory",
                        "griptape",
                    ],
                    "importance": 1.0,
                },
            )
        except Exception as e:
            raise RuntimeError(f"Failed to store memory in TIAMAT: {e}") from e

    def load(self) -> tuple[list[Run], dict[str, Any]]:
        """Load conversation runs from TIAMAT's cloud memory.

        Returns:
            Tuple of (runs list, metadata dict).
        """
        try:
            resp = self._client.post(
                "/api/memory/recall",
                json={
                    "query": f"agent:{self.agent_id} conversation_memory",
                    "limit": 1,
                },
            )

            if resp.status_code != 200:
                return [], {}

            memories = resp.json().get("memories", [])
            if not memories:
                return [], {}

            content = memories[0].get("content", "{}")
            params_dict = json.loads(content)
            return self._from_params_dict(params_dict)

        except Exception:
            return [], {}

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
