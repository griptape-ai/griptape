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
            retrieve the ID from the environment variable `GT_CLOUD_THREAD_ID`.
        alias: The alias of the Thread to store the conversation memory in.
        base_url: The base URL of the Griptape Cloud API. Defaults to the value of the environment variable
            `GT_CLOUD_BASE_URL` or `https://cloud.griptape.ai`.
        api_key: The API key to use for authenticating with the Griptape Cloud API. If not provided, the driver will
            attempt to retrieve the API key from the environment variable `GT_CLOUD_API_KEY`.

    Raises:
        ValueError: If `api_key` is not provided.
    """

    thread_id: Optional[str] = field(
        default=None,
        metadata={"serializable": True},
    )
    alias: Optional[str] = field(
        default=None,
        metadata={"serializable": True},
    )
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        init=False,
    )
    _thread: Optional[dict] = field(default=None, init=False)

    @api_key.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_api_key(self, _: Attribute, value: Optional[str]) -> str:
        if value is None:
            raise ValueError(f"{self.__class__.__name__} requires an API key")
        return value

    @property
    def thread(self) -> dict:
        """Try to get the Thread by ID, alias, or create a new one."""
        if self._thread is None:
            thread = None
            if self.thread_id is None:
                self.thread_id = os.getenv("GT_CLOUD_THREAD_ID")

            if self.thread_id is not None:
                res = self._call_api("get", f"/threads/{self.thread_id}", raise_for_status=False)
                if res.status_code == 200:
                    thread = res.json()

            # use name as 'alias' to get thread
            if thread is None and self.alias is not None:
                res = self._call_api("get", f"/threads?alias={self.alias}").json()
                if res.get("threads"):
                    thread = res["threads"][0]
                    self.thread_id = thread.get("thread_id")

            # no thread by name or thread_id
            if thread is None:
                data = {"name": uuid.uuid4().hex} if self.alias is None else {"name": self.alias, "alias": self.alias}
                thread = self._call_api("post", "/threads", data).json()
                self.thread_id = thread["thread_id"]
                self.alias = thread.get("alias")

            self._thread = thread

        return self._thread  # pyright: ignore[reportReturnType]

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
        thread_id = self.thread["thread_id"] if self.thread_id is None else self.thread_id
        self._call_api("patch", f"/threads/{thread_id}", body)
        self._thread = None

    def load(self) -> tuple[list[Run], dict[str, Any]]:
        from griptape.memory.structure import Run

        thread_id = self.thread["thread_id"] if self.thread_id is None else self.thread_id

        # get the Messages from the Thread
        messages_response = self._call_api("get", f"/threads/{thread_id}/messages").json()

        # retrieve the Thread to get the metadata
        thread_response = self._call_api("get", f"/threads/{thread_id}").json()

        runs = [
            Run(
                **({"id": message["metadata"].pop("run_id", None)} if "run_id" in message.get("metadata") else {}),
                meta=message["metadata"],
                input=BaseArtifact.from_json(message["input"]),
                output=BaseArtifact.from_json(message["output"]),
            )
            for message in messages_response.get("messages", [])
        ]

        return runs, thread_response.get("metadata", {})

    def _get_url(self, path: str) -> str:
        path = path.lstrip("/")
        return urljoin(self.base_url, f"/api/{path}")

    def _call_api(
        self, method: str, path: str, json: Optional[dict] = None, *, raise_for_status: bool = True
    ) -> requests.Response:
        res = requests.request(method, self._get_url(path), json=json, headers=self.headers)
        if raise_for_status:
            res.raise_for_status()
        return res
