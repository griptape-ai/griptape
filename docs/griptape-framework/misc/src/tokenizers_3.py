from griptape.tokenizers import AnthropicTokenizer

tokenizer = AnthropicTokenizer(model="claude-3-opus-20240229")

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
