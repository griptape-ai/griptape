import os

from griptape.tokenizers import GoogleTokenizer

tokenizer = GoogleTokenizer(model="gemini-pro", api_key=os.environ["GOOGLE_API_KEY"])

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
