from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Optional
from urllib.parse import urljoin

import requests
from attrs import Factory, define, field

from griptape.common import DeltaMessage, Message, PromptStack, observable
from griptape.configs.defaults_config import Defaults
from griptape.drivers.prompt import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, SimpleTokenizer

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy
    from griptape.tools.base_tool import BaseTool


logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class GriptapeCloudPromptDriver(BasePromptDriver):
    model: Optional[str] = field(default=None, kw_only=True)
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
    )
    api_key: str = field(default=Factory(lambda: os.environ["GT_CLOUD_API_KEY"]))
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(
            lambda self: SimpleTokenizer(
                characters_per_token=4,
                max_input_tokens=2000,
                max_output_tokens=self.max_tokens,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    use_native_tools: bool = field(default=True, kw_only=True)
    structured_output_strategy: StructuredOutputStrategy = field(
        default="native", kw_only=True, metadata={"serializable": True}
    )

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        url = urljoin(self.base_url.strip("/"), "/api/chat/messages")

        params = self._base_params(prompt_stack)
        logger.debug(params)
        response = requests.post(url, headers=self.headers, json=params)
        response.raise_for_status()
        response_json = response.json()
        logger.debug(response_json)

        return Message.from_dict(response_json)

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        url = urljoin(self.base_url.strip("/"), "/api/chat/messages/stream")
        params = self._base_params(prompt_stack)
        logger.debug(params)
        with requests.post(url, headers=self.headers, json=params, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data:"):
                        delta_message_payload = decoded_line.removeprefix("data:").strip()
                        logger.debug(delta_message_payload)
                        yield DeltaMessage.from_json(delta_message_payload)

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        return {
            "messages": prompt_stack.to_dict()["messages"],
            "tools": self.__to_griptape_tools(prompt_stack.tools),
            **({"output_schema": prompt_stack.to_output_json_schema()} if prompt_stack.output_schema else {}),
            "driver_configuration": {
                **({"model": self.model} if self.model else {}),
                "max_tokens": self.max_tokens,
                "use_native_tools": self.use_native_tools,
                "temperature": self.temperature,
                "structured_output_strategy": self.structured_output_strategy,
                "extra_params": self.extra_params,
            },
        }

    def __to_griptape_tools(self, tools: list[BaseTool]) -> list[dict]:
        return [
            {
                "name": tool.name,
                "activities": [
                    {
                        "name": activity.__name__,
                        "description": tool.activity_description(activity),
                        "json_schema": tool.to_activity_json_schema(activity, "Schema"),
                    }
                    for activity in tool.activities()
                ],
            }
            for tool in tools
        ]
