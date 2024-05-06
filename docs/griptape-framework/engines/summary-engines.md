## Overview

Summary engines are used to summarize text and collections of [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s.

## PromptSummaryEngine

Used to summarize texts with LLMs. You can set a custom [prompt_driver](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.prompt_driver), [template_generator](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.template_generator), and [chunker](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.chunker).

Use the [summarize_artifacts](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.summarize_artifacts) method to summarize a list of artifacts or [summarize_text](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.summarize_text) to summarize an arbitrary string.

```python
import io
import requests

from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import PromptSummaryEngine
from griptape.loaders import PdfLoader

response = requests.get("https://arxiv.org/pdf/1706.03762.pdf")
engine = PromptSummaryEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
)

artifacts = PdfLoader().load(response.content)

text = "\n\n".join([a.value for a in artifacts])

engine.summarize_text(text)
```
