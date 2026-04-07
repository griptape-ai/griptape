from griptape.tokenizers import AmazonBedrockTokenizer

tokenizer = AmazonBedrockTokenizer(model="amazon.titan-text-express-v1")

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
