from griptape.chunkers import TextChunker
from griptape.tokenizers import OpenAiTokenizer

TextChunker(
    # set an optional custom tokenizer
    tokenizer=OpenAiTokenizer(model="gpt-4.1"),
    # optionally modify default number of tokens
    max_tokens=100,
).chunk("long text")
