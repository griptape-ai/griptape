from griptape.tokenizers import SimpleTokenizer

tokenizer = SimpleTokenizer(max_input_tokens=1024, max_output_tokens=1024, characters_per_token=6)

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
