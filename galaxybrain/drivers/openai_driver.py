from attrs import define
from galaxybrain.drivers import Driver
from galaxybrain.workflows.step_output import StepOutput
import openai
import json


@define()
class OpenAiDriver(Driver):
    api_key: str = None
    model: str = "text-davinci-003"
    suffix: str = None
    max_tokens: int = 2000
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

    def run(self, prompt_value: str) -> StepOutput:
        if self.api_key:
            openai.api_key = self.api_key

        result = openai.Completion.create(
            model=self.model,
            prompt=prompt_value,
            suffix=self.suffix,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            stream=self.stream,
            logprobs=self.logprobs,
            echo=self.echo,
            stop=self.stop,
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
