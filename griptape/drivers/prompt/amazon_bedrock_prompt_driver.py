from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field
from schema import Schema

from griptape.artifacts import (
    ActionArtifact,
    BaseArtifact,
    ErrorArtifact,
    ImageArtifact,
    InfoArtifact,
    ListArtifact,
    TextArtifact,
)
from griptape.common import (
    ActionCallDeltaMessageContent,
    ActionCallMessageContent,
    ActionResultMessageContent,
    BaseDeltaMessageContent,
    BaseMessageContent,
    DeltaMessage,
    ImageMessageContent,
    Message,
    TextDeltaMessageContent,
    TextMessageContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import AmazonBedrockTokenizer, BaseTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3

    from griptape.common import PromptStack
    from griptape.tools import BaseTool


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
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    tool_choice: dict = field(default=Factory(lambda: {"auto": {}}), kw_only=True, metadata={"serializable": True})
    tool_schema_id: str = field(
        default="https://griptape.ai",  # Amazon Bedrock requires that this be a valid URL.
        kw_only=True,
        metadata={"serializable": True},
    )

    def try_run(self, prompt_stack: PromptStack) -> Message:
        response = self.bedrock_client.converse(**self._base_params(prompt_stack))

        usage = response["usage"]
        output_message = response["output"]["message"]

        return Message(
            content=[self.__message_content_to_prompt_stack_content(content) for content in output_message["content"]],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=usage["inputTokens"], output_tokens=usage["outputTokens"]),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        response = self.bedrock_client.converse_stream(**self._base_params(prompt_stack))

        stream = response.get("stream")
        if stream is not None:
            for event in stream:
                if "contentBlockDelta" in event or "contentBlockStart" in event:
                    yield DeltaMessage(content=self.__bedrock_message_content_delta_to_message_content_delta(event))
                elif "metadata" in event:
                    usage = event["metadata"]["usage"]
                    yield DeltaMessage(
                        usage=DeltaMessage.Usage(input_tokens=usage["inputTokens"], output_tokens=usage["outputTokens"])
                    )
        else:
            raise Exception("model response is empty")

    def _prompt_stack_messages_to_messages(self, messages: list[Message]) -> list[dict]:
        return [
            {
                "role": self.__to_role(message),
                "content": [self.__prompt_stack_content_message_content(content) for content in message.content],
            }
            for message in messages
        ]

    def _prompt_stack_to_tools(self, prompt_stack: PromptStack) -> dict:
        return (
            {"toolConfig": {"tools": self.__to_tools(prompt_stack.actions), "toolChoice": self.tool_choice}}
            if prompt_stack.actions and self.use_native_tools
            else {}
        )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        system_messages = [{"text": message.to_text()} for message in prompt_stack.system_messages]

        messages = self._prompt_stack_messages_to_messages(
            [message for message in prompt_stack.messages if not message.is_system()]
        )

        return {
            "modelId": self.model,
            "messages": messages,
            "system": system_messages,
            "inferenceConfig": {"temperature": self.temperature},
            "additionalModelRequestFields": self.additional_model_request_fields,
            **self._prompt_stack_to_tools(prompt_stack),
        }

    def __message_content_to_prompt_stack_content(self, content: dict) -> BaseMessageContent:
        if "text" in content:
            return TextMessageContent(TextArtifact(content["text"]))
        elif "toolUse" in content:
            name, path = content["toolUse"]["name"].split("_", 1)
            return ActionCallMessageContent(
                artifact=ActionArtifact(
                    value=ActionArtifact.Action(
                        tag=content["toolUse"]["toolUseId"], name=name, path=path, input=content["toolUse"]["input"]
                    )
                )
            )
        else:
            raise ValueError(f"Unsupported message content type: {content}")

    def __bedrock_message_content_delta_to_message_content_delta(self, event: dict) -> BaseDeltaMessageContent:
        if "contentBlockStart" in event:
            content_block = event["contentBlockStart"]["start"]

            if "toolUse" in content_block:
                name, path = content_block["toolUse"]["name"].split("_", 1)

                return ActionCallDeltaMessageContent(
                    index=event["contentBlockStart"]["contentBlockIndex"],
                    tag=content_block["toolUse"]["toolUseId"],
                    name=name,
                    path=path,
                )
            elif "text" in content_block:
                return TextDeltaMessageContent(
                    content_block["text"], index=event["contentBlockStart"]["contentBlockIndex"]
                )
            else:
                raise ValueError(f"Unsupported message content type: {event}")
        elif "contentBlockDelta" in event:
            content_block_delta = event["contentBlockDelta"]

            if "text" in content_block_delta["delta"]:
                return TextDeltaMessageContent(
                    content_block_delta["delta"]["text"], index=content_block_delta["contentBlockIndex"]
                )
            elif "toolUse" in content_block_delta["delta"]:
                return ActionCallDeltaMessageContent(
                    index=content_block_delta["contentBlockIndex"],
                    partial_input=content_block_delta["delta"]["toolUse"]["input"],
                )
            else:
                raise ValueError(f"Unsupported message content type: {event}")
        else:
            raise ValueError(f"Unsupported message content type: {event}")

    def __prompt_stack_content_message_content(self, content: BaseMessageContent) -> dict:
        if isinstance(content, TextMessageContent):
            return self.__artifact_to_message_content(content.artifact)
        elif isinstance(content, ImageMessageContent):
            return self.__artifact_to_message_content(content.artifact)
        elif isinstance(content, ActionCallMessageContent):
            action_call = content.artifact.value

            return {
                "toolUse": {
                    "toolUseId": action_call.tag,
                    "name": f"{action_call.name}_{action_call.path}",
                    "input": action_call.input,
                }
            }
        elif isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            if isinstance(artifact, ListArtifact):
                message_content = [self.__artifact_to_message_content(artifact) for artifact in artifact.value]
            else:
                message_content = [self.__artifact_to_message_content(artifact)]

            return {
                "toolResult": {
                    "toolUseId": content.action.tag,
                    "content": message_content,
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

    def __to_role(self, message: Message) -> str:
        if message.is_assistant():
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
                        "json": (tool.activity_schema(activity) or Schema({})).json_schema(self.tool_schema_id)
                    },
                }
            }
            for tool in tools
            for activity in tool.activities()
        ]
