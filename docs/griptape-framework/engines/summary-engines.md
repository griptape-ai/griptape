---
search:
  boost: 2 
---

## Overview

Summary engines are used to summarize text and collections of [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s.

## Prompt

Used to summarize texts with LLMs. You can set a custom [prompt_driver](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.prompt_driver), [system_template_generator](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.system_template_generator), [user_template_generator](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.user_template_generator), and [chunker](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.chunker).

Use the [summarize_artifacts](../../reference/griptape/engines/summary/prompt_summary_engine.md#griptape.engines.summary.prompt_summary_engine.PromptSummaryEngine.summarize_artifacts) method to summarize a list of artifacts or [summarize_text](../../reference/griptape/engines/summary/base_summary_engine.md#griptape.engines.summary.base_summary_engine.BaseSummaryEngine.summarize_text) to summarize an arbitrary string.

```python
--8<-- "docs/griptape-framework/engines/src/summary_engines_1.py"
```
