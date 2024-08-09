from griptape.tokenizers import OpenAiTokenizer

tokenizer = OpenAiTokenizer(model="gpt-4o")

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
