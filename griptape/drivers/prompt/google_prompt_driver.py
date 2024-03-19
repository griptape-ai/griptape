from __future__ import annotations
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional, Any
from attr import define, field, Factory
from griptape.utils import PromptStack, import_optional_dependency
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import GoogleTokenizer, BaseTokenizer

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel
    from google.generativeai.types import ContentDict


@define
class GooglePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Google API key.
        model: Google model name.
        model_client: Custom `GenerativeModel` client.
        tokenizer: Custom `GoogleTokenizer`.
        top_p: Optional value for top_p.
        top_k: Optional value for top_k.
    """

    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    model_client: Any = field(default=Factory(lambda self: self._default_model_client(), takes_self=True), kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        history, message = self._prompt_stack_to_model_input(prompt_stack)
        chat = self.model_client.start_chat(history=history)
        response = chat.send_message(
            message["parts"][0],
            generation_config=GenerationConfig(
                stop_sequences=self.tokenizer.stop_sequences,
                max_output_tokens=self.max_output_tokens(history + [message]),
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            ),
        )

        return TextArtifact(value=response.text)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        history, message = self._prompt_stack_to_model_input(prompt_stack)
        chat = self.model_client.start_chat(history=history)
        response = chat.send_message(
            message["parts"][0],
            stream=True,
            generation_config=GenerationConfig(
                stop_sequences=self.tokenizer.stop_sequences,
                max_output_tokens=self.max_output_tokens(history + [message]),
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            ),
        )

        for chunk in response:
            yield TextArtifact(value=chunk.text)

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)

    def _prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> tuple[list[ContentDict], ContentDict]:
        history_inputs = prompt_stack.inputs[:-1]
        message_input = self.__to_content_dict(prompt_stack.inputs[-1])

        history = []
        for prompt_input in history_inputs:
            if prompt_input.is_system():
                history.append(self.__to_content_dict(prompt_input))
                history.append(
                    self.__to_content_dict(PromptStack.Input(role=PromptStack.ASSISTANT_ROLE, content="Understood."))
                )
            elif prompt_input.is_assistant():
                history.append(self.__to_content_dict(prompt_input))
            else:
                history.append(self.__to_content_dict(prompt_input))

        return history, message_input

    def __to_content_dict(self, prompt_input: PromptStack.Input) -> ContentDict:
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict

        return ContentDict({"role": self.__to_google_role(prompt_input), "parts": [prompt_input.content]})

    def __to_google_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "user"
        elif prompt_input.is_assistant():
            return "model"
        else:
            return "user"
