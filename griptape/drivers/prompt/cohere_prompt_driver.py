import cohere
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import CohereTokenizer
from griptape.utils import PromptStack
from griptape.events import CompletionChunkEvent


@define
class CoherePromptDriver(BasePromptDriver):
    """
    Attributes: 
        api_key: Cohere API key.
        model: 	Cohere model name.
        client: Custom `cohere.Client`.
        tokenizer: Custom `CohereTokenizer`.
    """
    api_key: str = field(kw_only=True)
    model: str = field(kw_only=True)
    client: cohere.Client = field(
        default=Factory(lambda self: cohere.Client(self.api_key), takes_self=True), kw_only=True
    )
    tokenizer: CohereTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True),
        kw_only=True
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        prompt = self.prompt_stack_to_string(prompt_stack)
        result = self.client.generate(
            prompt=prompt,
            model=self.model,
            temperature=self.temperature,
            end_sequences=self.tokenizer.stop_sequences,
            max_tokens=self.max_output_tokens(prompt),
            stream=self.stream
        )

        
        if self.stream:
            tokens = []

            for chunk in result:
                text = chunk.text
                tokens.append(text)

                if self.structure:
                    self.structure.publish_event(
                        CompletionChunkEvent(token=text)
                    )
            full_message = ''.join(tokens)

            return TextArtifact(value=full_message)
        else:
            if len(result.generations) == 1:
                generation = result.generations[0]

                return TextArtifact(
                    value=generation.text.strip()
                )
            else:
                raise Exception("Completion with more than one choice is not supported yet.")
