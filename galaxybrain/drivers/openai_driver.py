import json
from typing import Optional
import openai
from attrs import define
from galaxybrain.drivers import CompletionDriver
from galaxybrain.utils import TiktokenTokenizer, Tokenizer
from galaxybrain.workflows.step_output import StepOutput


@define()
class OpenAiCompletionDriver(CompletionDriver):
    api_key: str = None
    model: Optional[str] = None
    suffix: str = None
    max_tokens: Optional[int] = None
    temperature: float = 0.5
    top_p: float = 1
    n: int = 1
    stream: bool = False
    logprobs: int = None
    echo: bool = False
    stop = None
    presence_penalty: int = 0
    frequency_penalty: int = 0
    best_of: int = 1
    logit_bias: map = {}
    user: str = ""
    tokenizer: Tokenizer = TiktokenTokenizer()

    def run(self, value: any) -> StepOutput:
        if self.api_key:
            openai.api_key = self.api_key

        if self.stop is None:
            stop = self.tokenizer.stop_token
        else:
            stop = self.stop

        if self.model is None:
            model = self.tokenizer.model
        else:
            model = self.model

        if self.max_tokens is None:
            tokens = TiktokenTokenizer(model).tokens_left(value)
        else:
            tokens = self.max_tokens

        result = openai.Completion.create(
            model=model,
            prompt=value,
            suffix=self.suffix,
            max_tokens=tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            stream=self.stream,
            logprobs=self.logprobs,
            echo=self.echo,
            stop=stop,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            best_of=self.best_of,
            logit_bias=self.logit_bias,
            user=self.user
        )

        if len(result.choices) == 1:
            return StepOutput(
                value=result.choices[0].text.strip(),
                meta={
                    "id": result["id"],
                    "created": result["created"],
                    "usage": json.dumps(result["usage"])
                }
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")
