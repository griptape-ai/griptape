from __future__ import annotations

import os
import uuid
from typing import TYPE_CHECKING, Optional
from urllib.parse import urljoin

import requests
from attrs import Attribute, Factory, define, field

from griptape.artifacts import BaseArtifact
from griptape.drivers import BaseConversationMemoryDriver

if TYPE_CHECKING:
    from griptape.memory.structure import BaseConversationMemory


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

    def store(self, memory: BaseConversationMemory) -> None:
        # serliaze the run artifacts to json strings
        messages = [{"input": run.input.to_json(), "output": run.output.to_json()} for run in memory.runs]

        # serialize the metadata to a json string
        # remove runs because they are already stored as Messages
        metadata = memory.to_dict()
        del metadata["runs"]

        # patch the Thread with the new messages and metadata
        # all old Messages are replaced with the new ones
        response = requests.patch(
            self._get_url(f"/threads/{self.thread_id}"),
            json={"messages": messages, "metadata": metadata},
            headers=self.headers,
        )
        response.raise_for_status()

    def load(self) -> BaseConversationMemory:
        from griptape.memory.structure import BaseConversationMemory, ConversationMemory, Run

        # get the Messages from the Thread
        messages_response = requests.get(self._get_url(f"/threads/{self.thread_id}/messages"), headers=self.headers)
        messages_response.raise_for_status()
        messages_response = messages_response.json()

        # retrieve the Thread to get the metadata
        thread_response = requests.get(self._get_url(f"/threads/{self.thread_id}"), headers=self.headers)
        thread_response.raise_for_status()
        thread_response = thread_response.json()

        messages = messages_response.get("messages", [])

        runs = [
            Run(
                id=m["message_id"],
                input=BaseArtifact.from_json(m["input"]),
                output=BaseArtifact.from_json(m["output"]),
            )
            for m in messages
        ]
        metadata = thread_response.get("metadata")

        # the metadata will contain the serialized
        # ConversationMemory object with the runs removed
        # autoload=False to prevent recursively loading the memory
        if metadata is not None and metadata != {}:
            memory = BaseConversationMemory.from_dict(
                {
                    **metadata,
                    "runs": [run.to_dict() for run in runs],
                    "autoload": False,
                }
            )
            memory.driver = self
            return memory
        # no metadata found, return a new ConversationMemory object
        return ConversationMemory(runs=runs, autoload=False, driver=self)

    def _get_thread_id(self) -> str:
        res = requests.post(self._get_url("/threads"), json={"name": uuid.uuid4().hex}, headers=self.headers)
        res.raise_for_status()
        return res.json().get("thread_id")

    def _get_url(self, path: str) -> str:
        path = path.lstrip("/")
        return urljoin(self.base_url, f"/api/{path}")
