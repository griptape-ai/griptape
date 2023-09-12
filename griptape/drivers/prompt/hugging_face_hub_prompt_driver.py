from os import environ

from griptape.utils import PromptStack

environ["TRANSFORMERS_VERBOSITY"] = "error"

from attr import define, field, Factory
from huggingface_hub import InferenceApi
from transformers import AutoTokenizer
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import HuggingFaceTokenizer


@define
class HuggingFaceHubPromptDriver(BasePromptDriver):
    """
    Attributes:
        repo_id: Hugging Face Hub repo ID. 
        api_token: Hugging Face Hub API token.
        use_gpu: Use GPU during model run.
        params: Custom model run parameters. 
        model: Hugging Face Hub model name. Defaults to `repo_id`.
        client: Custom `InferenceApi`.
        tokenizer: Custom `HuggingFaceTokenizer`.
        
    """
    SUPPORTED_TASKS = ["text2text-generation", "text-generation"]
    MAX_NEW_TOKENS = 250
    DEFAULT_PARAMS = {
        "return_full_text": False,
        "max_new_tokens": MAX_NEW_TOKENS
    }

    repo_id: str = field(kw_only=True)
    api_token: str = field(kw_only=True)
    use_gpu: bool = field(default=False, kw_only=True)
    params: dict = field(factory=dict, kw_only=True)
    model: str = field(default=Factory(lambda self: self.repo_id, takes_self=True), kw_only=True)
    client: InferenceApi = field(
        default=Factory(
            lambda self: InferenceApi(
                repo_id=self.repo_id,
                token=self.api_token,
                gpu=self.use_gpu
            ),
            takes_self=True
        ),
        kw_only=True
    )
    tokenizer: HuggingFaceTokenizer = field(
        default=Factory(
            lambda self: HuggingFaceTokenizer(
                tokenizer=AutoTokenizer.from_pretrained(self.repo_id),
                max_tokens=self.MAX_NEW_TOKENS
            ), takes_self=True
        ),
        kw_only=True
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        prompt = self.prompt_stack_to_string(prompt_stack)

        if self.client.task in self.SUPPORTED_TASKS:
            response = self.client(
                inputs=prompt,
                params=self.DEFAULT_PARAMS | self.params
            )

            if len(response) == 1:
                return TextArtifact(
                    value=response[0]["generated_text"].strip()
                )
            else:
                raise Exception("Completion with more than one choice is not supported yet.")
        else:
            raise Exception(f"Only models with the following tasks are supported: {self.SUPPORTED_TASKS}")
