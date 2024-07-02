from __future__ import annotations
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers.base_tokenizer import BaseTokenizer
from griptape.common import PromptStack, TextMessageContent
from griptape.utils import import_optional_dependency
from griptape.tokenizers import SimpleTokenizer
from griptape.common import Message, DeltaMessage, TextDeltaMessageContent
from griptape.common import ImageMessageContent

if TYPE_CHECKING:
    from ollama import Client


@define
class OllamaPromptDriver(BasePromptDriver):
    """
    Attributes:
        model: Model name.
    """

    model: str = field(kw_only=True, metadata={"serializable": True})
    host: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("ollama").Client(host=self.host), takes_self=True),
        kw_only=True,
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(
            lambda self: SimpleTokenizer(
                characters_per_token=4, max_input_tokens=2000, max_output_tokens=self.max_tokens
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    options: dict = field(
        default=Factory(
            lambda self: {
                "temperature": self.temperature,
                "stop": self.tokenizer.stop_sequences,
                "num_predict": self.max_tokens,
            },
            takes_self=True,
        ),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> Message:
        response = self.client.chat(**self._base_params(prompt_stack))

        if isinstance(response, dict):
            return Message(
                content=[TextMessageContent(TextArtifact(value=response["message"]["content"]))],
                role=Message.ASSISTANT_ROLE,
            )
        else:
            raise Exception("invalid model response")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        stream = self.client.chat(**self._base_params(prompt_stack), stream=True)

        if isinstance(stream, Iterator):
            for chunk in stream:
                yield DeltaMessage(content=TextDeltaMessageContent(chunk["message"]["content"]))
        else:
            raise Exception("invalid model response")

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        messages = self._prompt_stack_to_messages(prompt_stack)

        return {"messages": messages, "model": self.model, "options": self.options}

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        return [
            {
                "role": message.role,
                "content": message.to_text(),
                **(
                    {
                        "images": [
                            content.artifact.base64
                            for content in message.content
                            if isinstance(content, ImageMessageContent)
                        ]
                    }
                    if any(isinstance(content, ImageMessageContent) for content in message.content)
                    else {}
                ),
            }
            for message in prompt_stack.messages
        ]
