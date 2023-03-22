import json
import openai
from attrs import define, field, Factory
from warpspeed.drivers import PromptDriver
from warpspeed.utils import TiktokenTokenizer
from warpspeed.artifacts import TextOutput


@define
class OpenAiPromptDriver(PromptDriver):
    model: str = field(default=TiktokenTokenizer.DEFAULT_MODEL, kw_only=True)
    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda self: TiktokenTokenizer(model=self.model), takes_self=True),
        kw_only=True
    )
    temperature: float = field(default=0.5, kw_only=True)
    user: str = field(default="", kw_only=True)

    def try_run(self, value: any) -> TextOutput:
        if self.tokenizer.is_chat():
            return self.__run_chat(value)
        else:
            return self.__run_completion(value)

    def __run_chat(self, value: str) -> TextOutput:
        result = openai.ChatCompletion.create(
            model=self.tokenizer.model,
            messages=[
                {
                    "role": "user",
                    "content": value
                }
            ],
            max_tokens=self.tokenizer.tokens_left(value),
            temperature=self.temperature,
            stop=self.tokenizer.stop_sequence,
            user=self.user
        )

        if len(result.choices) == 1:
            return TextOutput(
                value=result.choices[0]["message"]["content"].strip(),
                meta={
                    "id": result["id"],
                    "created": result["created"],
                    "usage": json.dumps(result["usage"])
                }
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def __run_completion(self, value: str) -> TextOutput:
        result = openai.Completion.create(
            model=self.tokenizer.model,
            prompt=value,
            max_tokens=self.tokenizer.tokens_left(value),
            temperature=self.temperature,
            stop=self.tokenizer.stop_sequence,
            user=self.user
        )

        if len(result.choices) == 1:
            return TextOutput(
                value=result.choices[0].text.strip(),
                meta={
                    "id": result["id"],
                    "created": result["created"],
                    "usage": json.dumps(result["usage"])
                }
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")