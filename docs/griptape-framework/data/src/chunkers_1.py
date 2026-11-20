from griptape.chunkers import TextChunker
from griptape.tokenizers import SimpleTokenizer

text = "Red fox jumps. Blue bird sings.\n\nGreen fish swims. Gold cat sleeps."
tokenizer = SimpleTokenizer(characters_per_token=1)

for max_tokens in (20, 40):
    print(f"max_tokens={max_tokens}")
    chunks = TextChunker(tokenizer=tokenizer, max_tokens=max_tokens).chunk(text)
    for chunk in chunks:
        print(f"{tokenizer.count_tokens(chunk.value)}: {chunk.value!r}")
