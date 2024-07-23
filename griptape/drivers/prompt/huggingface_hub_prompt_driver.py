from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.common import DeltaMessage, Message, PromptStack, TextDeltaMessageContent, observable
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import HuggingFaceTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from collections.abc import Iterator

    from huggingface_hub import InferenceClient


@define
class HuggingFaceHubPromptDriver(BasePromptDriver):
    """Hugging Face Hub Prompt Driver.

    Attributes:
        api_token: Hugging Face Hub API token.
        use_gpu: Use GPU during model run.
        params: Custom model run parameters.
        model: Hugging Face Hub model name.
        client: Custom `InferenceApi`.
        tokenizer: Custom `HuggingFaceTokenizer`.
    """

    api_token: str = field(kw_only=True, metadata={"serializable": True})
    max_tokens: int = field(default=250, kw_only=True, metadata={"serializable": True})
    params: dict = field(factory=dict, kw_only=True, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: InferenceClient = field(
        default=Factory(
            lambda self: import_optional_dependency("huggingface_hub").InferenceClient(
                model=self.model,
                token=self.api_token,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    tokenizer: HuggingFaceTokenizer = field(
        default=Factory(
            lambda self: HuggingFaceTokenizer(model=self.model, max_output_tokens=self.max_tokens),
            takes_self=True,
        ),
        kw_only=True,
    )

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        prompt = self.prompt_stack_to_string(prompt_stack)

        response = self.client.text_generation(
            prompt,
            return_full_text=False,
            max_new_tokens=self.max_tokens,
            **self.params,
        )
        input_tokens = len(self.__prompt_stack_to_tokens(prompt_stack))
        output_tokens = len(self.tokenizer.tokenizer.encode(response))

        return Message(
            content=response,
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=input_tokens, output_tokens=output_tokens),
        )

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        prompt = self.prompt_stack_to_string(prompt_stack)

        response = self.client.text_generation(
            prompt,
            return_full_text=False,
            max_new_tokens=self.max_tokens,
            stream=True,
            **self.params,
        )

        input_tokens = len(self.__prompt_stack_to_tokens(prompt_stack))

        full_text = ""
        for token in response:
            full_text += token
            yield DeltaMessage(content=TextDeltaMessageContent(token, index=0))

        output_tokens = len(self.tokenizer.tokenizer.encode(full_text))
        yield DeltaMessage(usage=DeltaMessage.Usage(input_tokens=input_tokens, output_tokens=output_tokens))

    def prompt_stack_to_string(self, prompt_stack: PromptStack) -> str:
        return self.tokenizer.tokenizer.decode(self.__prompt_stack_to_tokens(prompt_stack))

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        messages = []
        for message in prompt_stack.messages:
            if len(message.content) == 1:
                messages.append({"role": message.role, "content": message.to_text()})
            else:
                raise ValueError("Invalid input content length.")

        return messages

    def __prompt_stack_to_tokens(self, prompt_stack: PromptStack) -> list[int]:
        messages = self._prompt_stack_to_messages(prompt_stack)
        tokens = self.tokenizer.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=True)

        if isinstance(tokens, list):
            return tokens  # pyright: ignore[reportReturnType] According to the [docs](https://huggingface.co/docs/transformers/main/en/internal/tokenization_utils#transformers.PreTrainedTokenizerBase.apply_chat_template), the return type is List[int].
        else:
            raise ValueError("Invalid output type.")
