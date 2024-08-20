---
search:
  boost: 2 
---

## Overview 

Tokenizers are used throughout Griptape to calculate the number of [tokens](https://learn.microsoft.com/en-us/semantic-kernel/prompt-engineering/tokens) in a piece of text.
They are particularly useful for ensuring that the LLM token limits are not exceeded.

Tokenizers are a low level abstraction that you will rarely interact with directly.

## Tokenizers

### OpenAI

```python
--8<-- "docs/griptape-framework/misc/src/tokenizers_1.py"
```

### Cohere
```python
--8<-- "docs/griptape-framework/misc/src/tokenizers_2.py"
```

### Anthropic

```python
--8<-- "docs/griptape-framework/misc/src/tokenizers_3.py"
```

### Google

```python
--8<-- "docs/griptape-framework/misc/src/tokenizers_4.py"
```

### Hugging Face
```python
--8<-- "docs/griptape-framework/misc/src/tokenizers_5.py"
```

### Amazon Bedrock
```python
--8<-- "docs/griptape-framework/misc/src/tokenizers_6.py"
```

### Simple
Not all LLM providers have a public tokenizer API. In this case, you can use the `SimpleTokenizer` to count tokens based on a simple heuristic. 

```python
--8<-- "docs/griptape-framework/misc/src/tokenizers_7.py"
```
