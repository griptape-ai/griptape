from __future__ import annotations

import logging
import os
import time
from typing import Optional
from urllib.parse import urljoin

import requests
from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.configs.defaults_config import Defaults
from griptape.drivers import BaseAssistantDriver
from griptape.events import BaseEvent, EventBus

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
    ruleset_ids: list[str] = field(factory=list, kw_only=True)
    additional_ruleset_ids: list[str] = field(factory=list, kw_only=True)
    knowledge_base_ids: list[str] = field(factory=list, kw_only=True)
    additional_knowledge_base_ids: list[str] = field(factory=list, kw_only=True)
    stream: bool = field(default=False, kw_only=True)
    poll_interval: int = field(default=1, kw_only=True)
    max_attempts: int = field(default=20, kw_only=True)

    def try_run(self, *args: BaseArtifact) -> BaseArtifact | InfoArtifact:
        url = urljoin(self.base_url.strip("/"), f"/api/assistants/{self.assistant_id}/runs")

        response = requests.post(
            url,
            json={
                "args": [arg.value for arg in args],
                "stream": self.stream,
                "thread_id": self.thread_id,
                "input": self.input,
                "ruleset_ids": self.ruleset_ids,
                "additional_ruleset_ids": self.additional_ruleset_ids,
                "knowledge_base_ids": self.knowledge_base_ids,
                "additional_knowledge_base_ids": self.additional_knowledge_base_ids,
            },
            headers=self.headers,
        )
        response.raise_for_status()
        response_json = response.json()

        return self._get_run_result(response_json["assistant_run_id"])

    def _get_run_result(self, assistant_run_id: str) -> BaseArtifact | InfoArtifact:
        events, next_offset = self._get_run_events(assistant_run_id)
        attempts = 0
        output = None

        while output is None and attempts < self.max_attempts:
            for event in events:
                if event["origin"] == "ASSISTANT":
                    event_payload = event["payload"]
                    try:
                        EventBus.publish_event(BaseEvent.from_dict(event_payload))
                    except ValueError as e:
                        logger.warning("Failed to deserialize event: %s", e)
                    if event["type"] == "FinishStructureRunEvent":
                        output = BaseArtifact.from_dict(event_payload["output_task_output"])

            if output is None and not events:
                time.sleep(self.poll_interval)
                attempts += 1
            events, next_offset = self._get_run_events(assistant_run_id, offset=next_offset)

        if output is None:
            raise TimeoutError("The assistant run did not finish in time.")

        return output

    def _get_run_events(self, assistant_run_id: str, offset: int = 0) -> tuple[list[dict], int]:
        url = urljoin(self.base_url.strip("/"), f"/api/assistant-runs/{assistant_run_id}/events")
        response = requests.get(url, headers=self.headers, params={"offset": offset})
        response.raise_for_status()

        response_json = response.json()

        events = response_json.get("events", [])
        next_offset = response_json.get("next_offset", 0)

        return events, next_offset
