from __future__ import annotations

import json
import logging
import os
import uuid
from typing import TYPE_CHECKING, Optional

import requests
from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.configs.defaults_config import Defaults
from griptape.drivers.assistant import BaseAssistantDriver
from griptape.events import BaseEvent, EventBus
from griptape.utils.griptape_cloud import griptape_cloud_url

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class GriptapeCloudAssistantDriver(BaseAssistantDriver):
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        kw_only=True,
    )
    input: Optional[str] = field(default=None, kw_only=True)
    assistant_id: str = field(kw_only=True)
    thread_id: Optional[str] = field(default=None, kw_only=True)
    thread_alias: Optional[str] = field(default=None, kw_only=True)
    ruleset_ids: Optional[list[str]] = field(default=None, kw_only=True)
    additional_ruleset_ids: list[str] = field(factory=list, kw_only=True)
    knowledge_base_ids: Optional[list[str]] = field(default=None, kw_only=True)
    additional_knowledge_base_ids: list[str] = field(factory=list, kw_only=True)
    structure_ids: Optional[list[str]] = field(default=None, kw_only=True)
    additional_structure_ids: list[str] = field(factory=list, kw_only=True)
    tool_ids: Optional[list[str]] = field(default=None, kw_only=True)
    additional_tool_ids: list[str] = field(factory=list, kw_only=True)
    stream: bool = field(default=False, kw_only=True)
    poll_interval: int = field(default=1, kw_only=True)
    max_attempts: int = field(default=20, kw_only=True)
    auto_create_thread: bool = field(default=True, kw_only=True)

    def try_run(self, *args: BaseArtifact) -> TextArtifact:
        if self.thread_id is None and self.auto_create_thread:
            self._create_or_find_thread(self.thread_alias)
        assistant_run_id = self._create_run(*args)
        run_result = self._get_run_result(assistant_run_id)

        run_result.meta.update(
            {"assistant_id": self.assistant_id, "assistant_run_id": assistant_run_id, "thread_id": self.thread_id}
        )

        return run_result

    def _create_or_find_thread(self, thread_alias: Optional[str] = None) -> None:
        if thread_alias is None:
            self.thread_id = self._create_thread()
        else:
            thread = self._find_thread_by_alias(thread_alias)

            if thread is None:
                self.thread_id = self._create_thread(thread_alias)
            else:
                self.thread_id = thread["thread_id"]

    def _create_thread(self, thread_alias: Optional[str] = None) -> str:
        url = griptape_cloud_url(self.base_url, "api/threads")

        body = {"name": uuid.uuid4().hex}
        if thread_alias is not None:
            body["alias"] = thread_alias

        response = requests.post(url, json=body, headers=self.headers)
        response.raise_for_status()
        return response.json()["thread_id"]

    def _create_run(self, *args: BaseArtifact) -> str:
        url = griptape_cloud_url(self.base_url, f"api/assistants/{self.assistant_id}/runs")

        response = requests.post(
            url,
            json={
                "args": [arg.value for arg in args],
                "stream": self.stream,
                "thread_id": self.thread_id,
                "input": self.input,
                **({"ruleset_ids": self.ruleset_ids} if self.ruleset_ids is not None else {}),
                "additional_ruleset_ids": self.additional_ruleset_ids,
                **({"knowledge_base_ids": self.knowledge_base_ids} if self.knowledge_base_ids is not None else {}),
                "additional_knowledge_base_ids": self.additional_knowledge_base_ids,
                **({"structure_ids": self.structure_ids} if self.structure_ids is not None else {}),
                "additional_structure_ids": self.additional_structure_ids,
                **({"tool_ids": self.tool_ids} if self.tool_ids is not None else {}),
                "additional_tool_ids": self.additional_tool_ids,
            },
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()["assistant_run_id"]

    def _get_run_result(self, assistant_run_id: str) -> TextArtifact:
        events = self._get_run_events(assistant_run_id)
        output = None

        for event in events:
            if event["origin"] == "ASSISTANT":
                event_payload = event["payload"]
                try:
                    EventBus.publish_event(BaseEvent.from_dict(event_payload))
                except ValueError as e:
                    logger.warning("Failed to deserialize event: %s", e)
                if event["type"] == "FinishStructureRunEvent":
                    output = TextArtifact.from_dict(event_payload["output_task_output"])

        if output is None:
            raise ValueError("Output not found.")

        return output

    def _get_run_events(self, assistant_run_id: str) -> Iterator[dict]:
        url = griptape_cloud_url(self.base_url, f"api/assistant-runs/{assistant_run_id}/events/stream")
        with requests.get(url, headers=self.headers, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data:"):
                        yield json.loads(decoded_line.removeprefix("data:").strip())

    def _find_thread_by_alias(self, thread_alias: str) -> Optional[dict]:
        url = griptape_cloud_url(self.base_url, "api/threads")
        response = requests.get(url, params={"alias": thread_alias}, headers=self.headers)
        response.raise_for_status()

        threads = response.json()["threads"]

        return next((thread for thread in threads if thread["alias"] == thread_alias), None)
