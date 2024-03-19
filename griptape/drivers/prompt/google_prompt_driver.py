from __future__ import annotations
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Optional
from attr import define, field, Factory
from griptape.utils import PromptStack, import_optional_dependency
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import GoogleTokenizer, BaseTokenizer

if TYPE_CHECKING:
    from google.generativeai.types import ContentDict
    from google.generativeai import GenerativeModel


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

    api_key: str = field(kw_only=True, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    model_client: GenerativeModel = field(default=None, kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})

    def __attrs_post_init__(self):
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        self.model_client = genai.GenerativeModel(self.model)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        input = self._prompt_stack_to_model_input(prompt_stack)
        chat = self.model_client.start_chat(history=input["history"])
        response = chat.send_message(
            input["message"],
            generation_config=GenerationConfig(
                stop_sequences=self.tokenizer.stop_sequences,
                max_output_tokens=self.max_output_tokens(self.prompt_stack_to_string(prompt_stack)),
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            ),
        )

        return TextArtifact(value=response.text)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        input = self._prompt_stack_to_model_input(prompt_stack)
        chat = self.model_client.start_chat(history=input["history"])
        response = chat.send_message(
            input["message"],
            stream=True,
            generation_config=GenerationConfig(
                stop_sequences=self.tokenizer.stop_sequences,
                max_output_tokens=self.max_output_tokens(self.prompt_stack_to_string(prompt_stack)),
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            ),
        )

        for chunk in response:
            yield TextArtifact(value=chunk.text)

    def _prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> dict[str, Any]:
        history_inputs = prompt_stack.inputs[:-1]
        message = prompt_stack.inputs[-1].content

        content = []
        system_message = None
        for prompt_input in history_inputs:
            if prompt_input.is_system():
                system_message = prompt_input.content
            elif prompt_input.is_assistant():
                content.append(self.__to_content_dict(prompt_input))
            else:
                content.append(self.__to_content_dict(prompt_input))

        if system_message is not None:
            if content:
                content[0]["parts"].insert(0, f"*{system_message}*")
            else:
                message = f"*{system_message}* {message}"

        return {"message": message, "history": content}

    def __to_content_dict(self, prompt_input: PromptStack.Input) -> ContentDict:
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict

        return ContentDict({"role": self.__to_google_role(prompt_input), "parts": [prompt_input.content]})

    def __to_google_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "model"
        else:
            return "user"
