---
search:
  boost: 2
---

## Overview

Chunkers are used to split arbitrarily long text into chunks of certain token length.
Each chunker has a tokenizer, a max token count, and a list of default separators used to split up text into [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s.
Different types of chunkers provide lists of separators for specific text shapes:

- [TextChunker](../../reference/griptape/chunkers/text_chunker.md): works on most texts.
- [PdfChunker](../../reference/griptape/chunkers/pdf_chunker.md): works on text from PDF docs.
- [MarkdownChunker](../../reference/griptape/chunkers/markdown_chunker.md) works on markdown text.

## Token budgets

`max_tokens` is a budget measured by the chunker's tokenizer, not a requested character count or an exact output length.
Text that already fits the budget is returned without splitting.
Longer text is split recursively, so chunks can be smaller than the budget.
Use a positive budget and select a tokenizer that matches the model consuming the chunks, such as `OpenAiTokenizer(model="gpt-4.1")` for an OpenAI model.
If `max_tokens` is omitted, it defaults to the selected tokenizer's maximum input token count.

This example deliberately uses `SimpleTokenizer(characters_per_token=1)` so its counts are easy to inspect.
Other tokenizers can count the same text differently; a token is not generally one character.
The same text is chunked with two budgets, and each real `TextArtifact`'s value and token count are printed:

```python
--8<-- "docs/griptape-framework/data/src/chunkers_1.py"
```

```text
max_tokens=20
14: 'Red fox jumps.'
16: 'Blue bird sings.'
17: 'Green fish swims.'
16: 'Gold cat sleeps.'
max_tokens=40
31: 'Red fox jumps. Blue bird sings.'
34: 'Green fish swims. Gold cat sleeps.'
```

## Separator priority

`TextChunker` tries these separators in order: `"\n\n"`, `"\n"`, `". "`, `"! "`, `"? "`, then `" "`.
For text over budget, it chooses the first usable separator and splits into two approximately balanced parts.
Each part is split again if needed, using that separator or a later one in the list.
If no separator can split a part, the chunker falls back to halving its characters and checking the resulting token counts recursively.
The budget still uses the tokenizer, even when the fallback split is character-based.

This ordering favors paragraph boundaries before line, sentence, and word boundaries.
It does not fill every chunk to exactly `max_tokens`, as the example's counts show.
You can supply a different ordered list with `separators=[ChunkSeparator(". "), ChunkSeparator(" ")]` when constructing a chunker, importing `ChunkSeparator` from `griptape.chunkers`.
Changing the order can change chunk boundaries even with the same text and budget.

By default, a separator is attached to the preceding split part.
`ChunkSeparator("|", is_prefix=True)` instead attaches it to the following part.
Split parts are stripped of surrounding whitespace, so whitespace separators at chunk boundaries are not necessarily retained.
Do not rely on joining chunk values to reproduce the original text byte for byte.

## Choosing a chunk size

The most common use of a Chunker is to split up a long text into smaller chunks for inserting into a Vector Database when doing Retrieval Augmented Generation (RAG).

- Start with the embedding model's input limit and tokenizer, leaving room for any text added before embedding.
- For retrieved chunks passed to an LLM, also account for instructions, the query, other retrieved chunks, and the response budget in its context window.
- Smaller chunks can isolate a specific passage; larger chunks can retain more surrounding context.
    Try representative documents and queries to check whether boundaries preserve the information your application needs.
- There is no universally optimal chunk size.
    Compare retrieval quality and context usage for your workload rather than assuming the largest allowed budget is best.

See [RagEngine](../../griptape-framework/engines/rag-engines.md) for more information on how to use Chunkers in RAG pipelines.
