from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

from griptape.artifacts.image_artifact import ImageArtifact
from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import (
    ActionCallMessageContent,
    BaseMessageContent,
    ImageMessageContent,
    Message,
    PromptStack,
    TextMessageContent,
)

if TYPE_CHECKING:
    from griptape.drivers.prompt import BasePromptDriver


def to_griptape_request(openai_request: dict) -> tuple[PromptStack, dict]:
    driver_args = {
        "model": openai_request["model"],
        "temperature": openai_request.get("temperature"),
        "max_tokens": openai_request.get("max_tokens"),
        "stream": openai_request.get("stream", False),
    }
    openai_messages = openai_request.get("messages", [])

    prompt_stack = PromptStack(
        messages=[
            Message(
                content=[_to_griptape_message_content(openai_message["content"])],
                role=_to_griptape_role(openai_message["role"]),
            )
            for openai_message in openai_messages
        ]
    )

    return prompt_stack, driver_args


def to_openai_response(prompt_driver: BasePromptDriver, message: Message) -> dict:
    return {
        "id": message.id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": prompt_driver.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": _to_openai_role(message.role),
                    "content": [_to_openai_message_content(content) for content in message.content],
                    "tool_calls": [
                        _to_openai_tool_call(action_call)
                        for action_call in message.content
                        if isinstance(action_call, ActionCallMessageContent)
                    ],
                },
                "logprobs": -1,
                "finish_reason": _to_openai_finish_reason(message),
            }
        ],
        "usage": _to_openai_usage(message),
    }


def _to_openai_role(griptape_role: str) -> str:
    if griptape_role == Message.USER_ROLE:
        return "user"
    elif griptape_role == Message.ASSISTANT_ROLE:
        return "assistant"
    elif griptape_role == Message.SYSTEM_ROLE:
        return "system"
    else:
        raise ValueError(f"Unsupported role: {griptape_role}")


def _to_openai_message_content(griptape_message_content: BaseMessageContent) -> dict | str:
    if isinstance(griptape_message_content, TextMessageContent):
        return griptape_message_content.artifact.value
    else:
        raise ValueError(f"Unsupported message content type: {type(griptape_message_content)}")


def _to_openai_tool_call(action_call: ActionCallMessageContent) -> dict:
    action = action_call.artifact.value
    return {
        "id": action_call.artifact.id,
        "type": "function",
        "function": {"name": f"{action.name}{action.path}", "arguments": action.input},
    }


def _to_openai_usage(message: Message) -> dict:
    return {
        "prompt_tokens": message.usage.input_tokens or 0,
        "completion_tokens": message.usage.output_tokens or 0,
        "total_tokens": (message.usage.input_tokens or 0) + (message.usage.output_tokens or 0),
        "completion_tokens_details": {
            "reasoning_tokens": -1,
            "accepted_prediction_tokens": -1,
            "rejected_prediction_tokens": -1,
        },
    }


def _to_openai_finish_reason(message: Message) -> str:
    return "stop" if message.has_any_content_type(ActionCallMessageContent) else "tool_calls"


def _to_griptape_role(openai_role: str) -> str:
    if openai_role == "user":
        return Message.USER_ROLE
    elif openai_role == "assistant":
        return Message.ASSISTANT_ROLE
    elif openai_role == "system" or openai_role == "developer":
        return Message.SYSTEM_ROLE
    else:
        raise ValueError(f"Unsupported role: {openai_role}")


def _to_griptape_message_content(openai_message_content: dict | str) -> BaseMessageContent:
    if isinstance(openai_message_content, dict):
        content_type = openai_message_content["type"]

        if content_type == "text":
            return TextMessageContent(TextArtifact(openai_message_content["text"]))
        elif content_type == "image_url":
            url = openai_message_content["url"]
            match = re.match(r"data:(.*?);base64,", url)

            if match:
                mime_type = match.group(1)
                image_format = mime_type.split("/")[1]
            else:
                raise ValueError("Invalid image URL")

            return ImageMessageContent(ImageArtifact(openai_message_content["url"], format=image_format))
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    else:
        return TextMessageContent(TextArtifact(openai_message_content))
