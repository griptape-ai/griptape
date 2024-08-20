import os

from cohere import Client

from griptape.tokenizers import CohereTokenizer

tokenizer = CohereTokenizer(model="command", client=Client(os.environ["COHERE_API_KEY"]))

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
