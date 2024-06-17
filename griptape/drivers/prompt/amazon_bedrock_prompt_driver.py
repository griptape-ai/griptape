from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any
import json

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact, ActionCallArtifact, ImageArtifact
from griptape.artifacts.base_artifact import BaseArtifact
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.artifacts.info_artifact import InfoArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.common import (
    BaseDeltaPromptStackContent,
    DeltaPromptStackMessage,
    PromptStackMessage,
    DeltaTextPromptStackContent,
    BasePromptStackContent,
    TextPromptStackContent,
    ImagePromptStackContent,
)
from griptape.common import ActionCallPromptStackContent
from griptape.common.prompt_stack.contents.action_result_prompt_stack_content import ActionResultPromptStackContent
from griptape.common.prompt_stack.contents.delta_action_call_prompt_stack_content import (
    DeltaActionCallPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AmazonBedrockTokenizer, BaseTokenizer
from griptape.utils import import_optional_dependency
from schema import Schema

if TYPE_CHECKING:
    import boto3

    from griptape.tools import BaseTool
    from griptape.common import PromptStack


@define
class AmazonBedrockPromptDriver(BasePromptDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True), kw_only=True
    )
    additional_model_request_fields: dict = field(default=Factory(dict), kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: AmazonBedrockTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    use_native_tools: bool = field(default=True, kw_only=True)
    tool_choice: dict = field(default=Factory(lambda: {"auto": {}}), kw_only=True, metadata={"serializable": False})

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        response = self.bedrock_client.converse(**self._base_params(prompt_stack))

        usage = response["usage"]
        output_message = response["output"]["message"]

        return PromptStackElement(
            content=[self.__message_content_to_prompt_stack_content(content) for content in output_message["content"]],
            role=PromptStackElement.ASSISTANT_ROLE,
            usage=PromptStackElement.Usage(input_tokens=usage["inputTokens"], output_tokens=usage["outputTokens"]),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage | BaseDeltaPromptStackContent]:
        response = self.bedrock_client.converse_stream(**self._base_params(prompt_stack))

        stream = response.get("stream")
        if stream is not None:
            for event in stream:
                if "messageStart" in event:
                    yield DeltaPromptStackElement(role=PromptStackElement.ASSISTANT_ROLE)
                elif "contentBlockDelta" in event or "contentBlockStart" in event:
                    yield self.__message_content_delta_to_prompt_stack_content_delta(event)
                elif "metadata" in event:
                    usage = event["metadata"]["usage"]
                    yield DeltaPromptStackMessage(
                        delta_usage=DeltaPromptStackMessage.DeltaUsage(
                            input_tokens=usage["inputTokens"], output_tokens=usage["outputTokens"]
                        )
                    )
        else:
            raise Exception("model response is empty")

    def _prompt_stack_messages_to_messages(self, elements: list[PromptStackMessage]) -> list[dict]:
        return [
            {
                "role": self.__to_role(input),
                "content": [self.__prompt_stack_content_message_content(content) for content in input.content],
            }
            for input in elements
        ]

    def _prompt_stack_to_tools(self, prompt_stack: PromptStack) -> dict:
        return (
            {"toolConfig": {"tools": self.__to_tools(prompt_stack.actions), "toolChoice": self.tool_choice}}
            if prompt_stack.actions and self.use_native_tools
            else {}
        )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        system_messages = [
            {"text": input.to_text_artifact().to_text()} for input in prompt_stack.messages if input.is_system()
        ]

        messages = self._prompt_stack_messages_to_messages(
            [input for input in prompt_stack.messages if not input.is_system()]
        )

        return {
            "modelId": self.model,
            "messages": messages,
            "system": system_messages,
            "inferenceConfig": {"temperature": self.temperature},
            "additionalModelRequestFields": self.additional_model_request_fields,
            **self._prompt_stack_to_tools(prompt_stack),
        }

    def __message_content_to_prompt_stack_content(self, content: dict) -> BasePromptStackContent:
        if "text" in content:
            return TextPromptStackContent(TextArtifact(content["text"]))
        elif "toolUse" in content:
            name, path = content["toolUse"]["name"].split("_", 1)
            return ActionCallPromptStackContent(
                artifact=ActionCallArtifact(
                    value=ActionCallArtifact.ActionCall(
                        tag=content["toolUse"]["toolUseId"],
                        name=name,
                        path=path,
                        input=json.dumps(content["toolUse"]["input"]),
                    )
                )
            )
        else:
            raise ValueError(f"Unsupported message content type: {content}")

    def __message_content_delta_to_prompt_stack_content_delta(self, event: dict) -> BaseDeltaPromptStackContent:
        if "contentBlockStart" in event:
            content_block = event["contentBlockStart"]["start"]

            if "toolUse" in content_block:
                name, path = content_block["toolUse"]["name"].split("_", 1)

                return DeltaActionCallPromptStackContent(
                    index=event["contentBlockStart"]["contentBlockIndex"],
                    tag=content_block["toolUse"]["toolUseId"],
                    name=name,
                    path=path,
                )
            else:
                raise ValueError(f"Unsupported message content type: {event}")
        elif "contentBlockDelta" in event:
            content_block_delta = event["contentBlockDelta"]

            if "text" in content_block_delta["delta"]:
                return DeltaTextPromptStackContent(
                    content_block_delta["delta"]["text"], index=content_block_delta["contentBlockIndex"]
                )
            elif "toolUse" in content_block_delta["delta"]:
                return DeltaActionCallPromptStackContent(
                    index=content_block_delta["contentBlockIndex"],
                    delta_input=content_block_delta["delta"]["toolUse"]["input"],
                )
            else:
                raise ValueError(f"Unsupported message content type: {event}")
        else:
            raise ValueError(f"Unsupported message content type: {event}")

    def __prompt_stack_content_message_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return self.__artifact_to_message_content(content.artifact)
        elif isinstance(content, ImagePromptStackContent):
            return self.__artifact_to_message_content(content.artifact)
        elif isinstance(content, ActionCallPromptStackContent):
            action_call = content.artifact.value

            return {
                "toolUse": {
                    "toolUseId": action_call.tag,
                    "name": f"{action_call.name}_{action_call.path}",
                    "input": json.loads(action_call.input),
                }
            }
        elif isinstance(content, ActionResultPromptStackContent):
            artifact = content.artifact

            return {
                "toolResult": {
                    "toolUseId": content.action_tag,
                    "content": [self.__artifact_to_message_content(artifact) for artifact in artifact.value]
                    if isinstance(artifact, ListArtifact)
                    else [self.__artifact_to_message_content(artifact)],
                    "status": "error" if isinstance(artifact, ErrorArtifact) else "success",
                }
            }
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __artifact_to_message_content(self, artifact: BaseArtifact) -> dict:
        if isinstance(artifact, ImageArtifact):
            return {"image": {"format": artifact.format, "source": {"bytes": artifact.value}}}
        elif (
            isinstance(artifact, TextArtifact)
            or isinstance(artifact, ErrorArtifact)
            or isinstance(artifact, InfoArtifact)
        ):
            return {"text": artifact.to_text()}
        elif isinstance(artifact, ErrorArtifact):
            return {"text": artifact.to_text()}
        else:
            raise ValueError(f"Unsupported artifact type: {type(artifact)}")

    def __to_role(self, input: PromptStackElement) -> str:
        if input.is_system():
            return "system"
        elif input.is_assistant():
            return "assistant"
        else:
            return "user"

    def __to_tools(self, tools: list[BaseTool]) -> list[dict]:
        return [
            {
                "toolSpec": {
                    "name": f"{tool.name}_{tool.activity_name(activity)}",
                    "description": tool.activity_description(activity),
                    "inputSchema": {
                        "json": (tool.activity_schema(activity) or Schema({})).json_schema(
                            "https://griptape.ai"
                        )  # TODO: Allow for non-griptape ids
                    },
                }
            }
            for tool in tools
            for activity in tool.activities()
        ]
