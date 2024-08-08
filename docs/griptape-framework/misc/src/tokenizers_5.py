from griptape.tokenizers import HuggingFaceTokenizer

tokenizer = HuggingFaceTokenizer(
    model="sentence-transformers/all-MiniLM-L6-v2",
    max_output_tokens=512,
)

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
