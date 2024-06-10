from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, GoogleTokenizer
from griptape.utils import import_optional_dependency
from griptape.common import (
    PromptStackElement,
    DeltaPromptStackElement,
    BaseDeltaPromptStackContent,
    DeltaTextPromptStackContent,
)

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel
    from google.generativeai.types import ContentDict, GenerationConfig, GenerateContentResponse


@define
class GooglePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Google API key.
        model: Google model name.
        model_client: Custom `GenerativeModel` client.
        top_p: Optional value for top_p.
        top_k: Optional value for top_k.
    """

    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    model_client: Any = field(default=Factory(lambda self: self._default_model_client(), takes_self=True), kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        inputs = self._prompt_stack_to_model_input(prompt_stack)
        response: GenerateContentResponse = self.model_client.generate_content(
            inputs,
            generation_config=GenerationConfig(
                stop_sequences=self.tokenizer.stop_sequences,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            ),
        )

        candidates = response.candidates
        usage_metadata = response.usage_metadata  # pyright: ignore[reportAttributeAccessIssue]

        if len(candidates) == 1:
            content = candidates[0].content
            content_parts = content.parts
            content_role = content.role

            return PromptStackElement(
                content=[self.tokenizer.message_content_to_prompt_stack_content(part) for part in content_parts],
                role=content_role,
                usage=PromptStackElement.Usage(
                    input_tokens=usage_metadata.prompt_token_count, output_tokens=usage_metadata.candidates_token_count
                ),
            )
        else:
            raise Exception("Completion with more than one candidate is not supported.")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        inputs = self._prompt_stack_to_model_input(prompt_stack)
        response: GenerationConfig = self.model_client.generate_content(
            inputs,
            stream=True,
            generation_config=GenerationConfig(
                stop_sequences=self.tokenizer.stop_sequences,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
            ),
        )

        for chunk in response:
            yield DeltaTextPromptStackContent(TextArtifact(chunk.text), index=chunk.index)

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)

    def _prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> list[ContentDict]:
        inputs = [
            self.__to_content_dict(prompt_input) for prompt_input in prompt_stack.inputs if not prompt_input.is_system()
        ]

        # Gemini does not have the notion of a system message, so we insert it as part of the first message in the history.
        system = next((i for i in prompt_stack.inputs if i.is_system()), None)
        if system is not None:
            inputs[0]["parts"].insert(0, "\n".join(content.to_text() for content in system.content))

        return inputs

    def __to_content_dict(self, prompt_input: PromptStackElement) -> ContentDict:
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict
        message = self.tokenizer.prompt_stack_input_to_message(prompt_input)

        return ContentDict(message)
