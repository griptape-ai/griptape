import json
import openai
from attrs import define, field, Factory
from warpspeed.drivers import PromptDriver
from warpspeed.utils import TiktokenTokenizer, Tokenizer
from warpspeed.artifacts import TextOutput


@define()
class OpenAiPromptDriver(PromptDriver):
    tokenizer: Tokenizer = field(default=Factory(lambda: TiktokenTokenizer()), kw_only=True)
    temperature: float = field(default=0.5, kw_only=True)
    user: str = field(default="", kw_only=True)

    def run(self, value: any) -> TextOutput:
        result = openai.Completion.create(
            model=self.tokenizer.model,
            prompt=value,
            max_tokens=self.tokenizer.tokens_left(value),
            temperature=self.temperature,
            stop=self.tokenizer.stop_token,
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
