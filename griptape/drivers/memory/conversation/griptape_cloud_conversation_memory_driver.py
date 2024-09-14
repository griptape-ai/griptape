from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urljoin

import requests
from attrs import Attribute, Factory, define, field

from griptape.artifacts import BaseArtifact
from griptape.drivers import BaseConversationMemoryDriver
from griptape.utils import dict_merge

if TYPE_CHECKING:
    from griptape.memory.structure import Run


@define(kw_only=True)
class GriptapeCloudConversationMemoryDriver(BaseConversationMemoryDriver):
    """A driver for storing conversation memory in the Griptape Cloud.

    Attributes:
        thread_id: The ID of the Thread to store the conversation memory in. If not provided, the driver will attempt to
            retrieve the ID from the environment variable `GT_CLOUD_THREAD_ID`. If that is not set, a new Thread will be
            created.
        base_url: The base URL of the Griptape Cloud API. Defaults to the value of the environment variable
            `GT_CLOUD_BASE_URL` or `https://cloud.griptape.ai`.
        api_key: The API key to use for authenticating with the Griptape Cloud API. If not provided, the driver will
            attempt to retrieve the API key from the environment variable `GT_CLOUD_API_KEY`.

    Raises:
        ValueError: If `api_key` is not provided.
    """

    thread_id: str = field(
        default=None,
        metadata={"serializable": True},
    )
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: Optional[str] = field(default=Factory(lambda: os.getenv("GT_CLOUD_API_KEY")))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        init=False,
    )

    def __attrs_post_init__(self) -> None:
        if self.thread_id is None:
            self.thread_id = os.getenv("GT_CLOUD_THREAD_ID", self._get_thread_id())

    @api_key.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_api_key(self, _: Attribute, value: Optional[str]) -> str:
        if value is None:
            raise ValueError(f"{self.__class__.__name__} requires an API key")
        return value

    def store(self, runs: list[Run], metadata: dict[str, Any]) -> None:
        # serialize the run artifacts to json strings
        messages = [
            dict_merge(
                {
                    "input": run.input.to_json(),
                    "output": run.output.to_json(),
                    "metadata": {"run_id": run.id},
                },
                run.meta,
            )
            for run in runs
        ]

        body = dict_merge(
            {
                "messages": messages,
            },
            metadata,
        )

        # patch the Thread with the new messages and metadata
        # all old Messages are replaced with the new ones
        response = requests.patch(
            self._get_url(f"/threads/{self.thread_id}"),
            json=body,
            headers=self.headers,
        )
        response.raise_for_status()

    def load(self) -> tuple[list[Run], dict[str, Any]]:
        from griptape.memory.structure import Run

        # get the Messages from the Thread
        messages_response = requests.get(self._get_url(f"/threads/{self.thread_id}/messages"), headers=self.headers)
        messages_response.raise_for_status()
        messages_response = messages_response.json()

        # retrieve the Thread to get the metadata
        thread_response = requests.get(self._get_url(f"/threads/{self.thread_id}"), headers=self.headers)
        thread_response.raise_for_status()
        thread_response = thread_response.json()

        runs = [
            Run(
                id=m["metadata"].pop("run_id"),
                meta=m["metadata"],
                input=BaseArtifact.from_json(m["input"]),
                output=BaseArtifact.from_json(m["output"]),
            )
            for m in messages_response.get("messages", [])
        ]
        return runs, thread_response.get("metadata", {})

    def _get_thread_id(self) -> str:
        res = requests.post(self._get_url("/threads"), json={"name": uuid.uuid4().hex}, headers=self.headers)
        res.raise_for_status()
        return res.json().get("thread_id")

    def _get_url(self, path: str) -> str:
        path = path.lstrip("/")
        return urljoin(self.base_url, f"/api/{path}")
