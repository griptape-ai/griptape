# TaskMemoryClient

This tool enables LLMs to query and summarize task outputs that are stored in short-term tool memory. This tool uniquely requires the user to set the `off_prompt` property explicitly for usability reasons (Griptape doesn't provide the default `True` value).

```python
--8<-- "docs/griptape-tools/official-tools/src/task_memory_client_1.py"
```
