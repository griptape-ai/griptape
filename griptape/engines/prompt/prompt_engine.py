from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.common import (
    ActionCallDeltaMessageContent,
    ActionCallMessageContent,
    BaseDeltaMessageContent,
    DeltaMessage,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
)
from griptape.events import CompletionChunkEvent, FinishPromptEvent, StartPromptEvent
from griptape.mixins import EventPublisherMixin, ExponentialBackoffMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
    from griptape.tokenizers.base_tokenizer import BaseTokenizer


@define(kw_only=True)
class PromptEngine(SerializableMixin, ExponentialBackoffMixin, EventPublisherMixin, ABC):
    prompt_driver: BasePromptDriver = field(metadata={"serializable": True})
    stream: bool = field(default=False, kw_only=True, metadata={"serializable": True})

    @property
    def tokenizer(self) -> BaseTokenizer:
        return self.prompt_driver.tokenizer

    def before_run(self, prompt_stack: PromptStack) -> None:
        self.publish_event(StartPromptEvent(model=self.prompt_driver.model, prompt_stack=prompt_stack))

    def after_run(self, result: Message) -> None:
        self.publish_event(
            FinishPromptEvent(
                model=self.prompt_driver.model,
                result=result.value,
                input_token_count=result.usage.input_tokens,
                output_token_count=result.usage.output_tokens,
            ),
        )

    def run(self, prompt_stack: PromptStack) -> Message:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompt_stack)

                result = self.__process_stream(prompt_stack) if self.stream else self.__process_run(prompt_stack)

                self.after_run(result)

                return result
        else:
            raise Exception("prompt driver failed after all retry attempts")

    def __process_run(self, prompt_stack: PromptStack) -> Message:
        return self.prompt_driver.run(prompt_stack)

    def __process_stream(self, prompt_stack: PromptStack) -> Message:
        delta_contents: dict[int, list[BaseDeltaMessageContent]] = {}
        usage = DeltaMessage.Usage()

        # Aggregate all content deltas from the stream
        message_deltas = self.prompt_driver.stream(prompt_stack)
        for message_delta in message_deltas:
            usage += message_delta.usage
            content = message_delta.content

            if content is not None:
                if content.index in delta_contents:
                    delta_contents[content.index].append(content)
                else:
                    delta_contents[content.index] = [content]
                if isinstance(content, TextDeltaMessageContent):
                    self.publish_event(CompletionChunkEvent(token=content.text))
                elif isinstance(content, ActionCallDeltaMessageContent):
                    if content.tag is not None and content.name is not None and content.path is not None:
                        self.publish_event(CompletionChunkEvent(token=str(content)))
                    elif content.partial_input is not None:
                        self.publish_event(CompletionChunkEvent(token=content.partial_input))

        # Build a complete content from the content deltas
        result = self.__build_message(list(delta_contents.values()), usage)

        return result

    def __build_message(
        self, delta_contents: list[list[BaseDeltaMessageContent]], usage: DeltaMessage.Usage
    ) -> Message:
        content = []
        for delta_content in delta_contents:
            text_deltas = [delta for delta in delta_content if isinstance(delta, TextDeltaMessageContent)]
            action_deltas = [delta for delta in delta_content if isinstance(delta, ActionCallDeltaMessageContent)]

            if text_deltas:
                content.append(TextMessageContent.from_deltas(text_deltas))
            if action_deltas:
                content.append(ActionCallMessageContent.from_deltas(action_deltas))

        result = Message(
            content=content,
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
        )

        return result
