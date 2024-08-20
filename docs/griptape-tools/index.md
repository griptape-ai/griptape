Tools give the LLM abilities to invoke outside APIs, reference data sets, and generally expand their capabilities.

Griptape tools are special Python classes that LLMs can use to accomplish specific goals. Here is an example custom tool for generating a random number:

```python
--8<-- "docs/griptape-tools/src/index_1.py"
```

A tool can have many "activities" as denoted by the `@activity` decorator. Each activity has a description (used to provide context to the LLM), and the input schema that the LLM must follow in order to use the tool.

Output artifacts from all tool activities (except for `InfoArtifact` and `ErrorArtifact`) go to short-term `TaskMemory`. To disable that behavior set the `off_prompt` tool parameter to `False`:

We provide a set of official Griptape Tools for accessing and processing data. You can also [build your own tools](./custom-tools/index.md).
