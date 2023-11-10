from typing import Optional, Iterator
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer
from typing import Tuple, Type
import openai


@define
class OpenAiCompletionPromptDriver(BasePromptDriver):
    """
    Attributes:
        base_url: An optional OpenAi API URL.
        api_key: An optional OpenAi API key. If not provided, the `OPENAI_API_KEY` environment variable will be used.
        organization: An optional OpenAI organization. If not provided, the `OPENAI_ORG_ID` environment variable will be used.
        client: An `openai.OpenAI` client.
        model: An OpenAI model name.
        tokenizer: An `OpenAiTokenizer`.
        user: A user id. Can be used to track requests by user.
        ignored_exception_types: An optional tuple of exception types to ignore. Defaults to OpenAI's known exception types.
    """

    base_url: Optional[str] = field(default=None, kw_only=True)
    api_key: Optional[str] = field(default=None, kw_only=True)
    organization: Optional[str] = field(default=None, kw_only=True)
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        )
    )
    model: str = field(kw_only=True)
    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    user: str = field(default="", kw_only=True)
    ignored_exception_types: Tuple[Type[Exception], ...] = field(
        default=Factory(
            lambda: (
                openai.BadRequestError,
                openai.AuthenticationError,
                openai.PermissionDeniedError,
                openai.NotFoundError,
                openai.ConflictError,
                openai.UnprocessableEntityError,
            )
        ),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        result = self.client.completions.create(**self._base_params(prompt_stack))

        if len(result.choices) == 1:
            return TextArtifact(value=result.choices[0].text.strip())
        else:
            raise Exception("completion with more than one choice is not supported yet")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        result = self.client.completions.create(**self._base_params(prompt_stack), stream=True)

        for chunk in result:
            if len(chunk.choices) == 1:
                choice = chunk.choices[0]
                delta_content = choice.text
                yield TextArtifact(value=delta_content)

            else:
                raise Exception("completion with more than one choice is not supported yet")

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_string(prompt_stack)

        return {
            "model": self.model,
            "max_tokens": self.max_output_tokens(prompt),
            "temperature": self.temperature,
            "stop": self.tokenizer.stop_sequences,
            "user": self.user,
            "prompt": prompt,
        }
