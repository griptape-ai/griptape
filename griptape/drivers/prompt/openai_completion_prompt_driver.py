from typing import Optional, Iterator, Tuple, Type
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer
from griptape.processors.base_processors import BasePromptStackProcessor
from griptape.processors.amazon_comprehend_processor import AmazonComprehendPiiProcessor
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
    pii_processor: BasePromptStackProcessor = field(default=AmazonComprehendPiiProcessor(), kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        processed_prompt_stack = self.pii_processor.before_run(prompt_stack)
        result = self.client.completions.create(**self._base_params(processed_prompt_stack))
        processed_result = self.pii_processor.after_run(result)

        if len(processed_result.choices) == 1:
            return TextArtifact(value=processed_result.choices[0].text.strip())
        else:
            raise Exception("completion with more than one choice is not supported yet")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        processed_prompt_stack = self.pii_processor.before_run(prompt_stack)
        result = self.client.completions.create(**self._base_params(processed_prompt_stack), stream=True)

        for chunk in result:
            processed_chunk = self.pii_processor.after_run(chunk)

            if len(processed_chunk.choices) == 1:
                choice = processed_chunk.choices[0]
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
