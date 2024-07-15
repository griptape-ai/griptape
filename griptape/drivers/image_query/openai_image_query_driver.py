from __future__ import annotations

from typing import Literal, Optional

import openai
from attrs import Factory, define, field
from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartParam,
    ChatCompletionContentPartTextParam,
    ChatCompletionUserMessageParam,
)

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.image_query.base_image_query_driver import BaseImageQueryDriver


@define
class OpenAiImageQueryDriver(BaseImageQueryDriver):
    model: str = field(kw_only=True, metadata={"serializable": True})
    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True, metadata={"serializable": True})
    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True, metadata={"serializable": True})
    image_quality: Literal["auto", "low", "high"] = field(default="auto", kw_only=True, metadata={"serializable": True})
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        ),
    )

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        message_parts: list[ChatCompletionContentPartParam] = [
            ChatCompletionContentPartTextParam(type="text", text=query),
        ]

        for image in images:
            message_parts.append(
                ChatCompletionContentPartImageParam(
                    type="image_url",
                    image_url={"url": f"data:{image.mime_type};base64,{image.base64}", "detail": self.image_quality},
                ),
            )

        messages = ChatCompletionUserMessageParam(content=message_parts, role="user")
        params = {"model": self.model, "messages": [messages], "max_tokens": self.max_tokens}

        response = self.client.chat.completions.create(**params)

        if len(response.choices) != 1:
            raise Exception("Image query responses with more than one choice are not supported yet.")

        return TextArtifact(response.choices[0].message.content)
