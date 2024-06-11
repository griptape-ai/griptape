## Overview 

Tokenizers are used throughout Griptape to calculate the number of [tokens](https://learn.microsoft.com/en-us/semantic-kernel/prompt-engineering/tokens) in a piece of text.
They are particulary useful for ensuring that the LLM token limits are not exceeded.

Tokenizers are a low level abstraction that you will rarely interact with directly.

## Tokenizers

### OpenAI

```python
from griptape.tokenizers import OpenAiTokenizer


tokenizer = OpenAiTokenizer(model="gpt-4o")

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
```

### Cohere
```python
import os
from cohere import Client
from griptape.tokenizers import CohereTokenizer


tokenizer = CohereTokenizer(
    model="command", client=Client(os.environ["COHERE_API_KEY"])
)

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
```

### Anthropic

```python
from griptape.tokenizers import AnthropicTokenizer


tokenizer = AnthropicTokenizer(model="claude-3-opus-20240229")

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
```

### Google

```python
import os
from griptape.tokenizers import GoogleTokenizer

tokenizer = GoogleTokenizer(model="gemini-pro", api_key=os.environ["GOOGLE_API_KEY"])

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
```

### Hugging Face
```python
from transformers import AutoTokenizer
from griptape.tokenizers import HuggingFaceTokenizer


tokenizer = HuggingFaceTokenizer(
    model="sentence-transformers/all-MiniLM-L6-v2",
    max_output_tokens=512,
)

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
```

### Amazon Bedrock
```python
from griptape.tokenizers import AmazonBedrockTokenizer


tokenizer = AmazonBedrockTokenizer(model="amazon.titan-text-express-v1")

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
```

### Simple
Not all LLM providers have a public tokenizer API. In this case, you can use the `SimpleTokenizer` to count tokens based on a simple heuristic. 

```python
from griptape.tokenizers import SimpleTokenizer

tokenizer = SimpleTokenizer(max_input_tokens=1024, max_output_tokens=1024, characters_per_token=6)

print(tokenizer.count_tokens("Hello world!"))
print(tokenizer.count_input_tokens_left("Hello world!"))
print(tokenizer.count_output_tokens_left("Hello world!"))
```
