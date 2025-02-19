import os

from griptape.tokenizers import GrokTokenizer

tokenizer = GrokTokenizer(
    model="grok-2-latest",
    api_key=os.environ["GROK_API_KEY"],
)

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
