---
search:
  boost: 2
---

## Overview

Rerank Drivers can be used to rerank search results for a particular query. Every Rerank Driver implements the following methods that can be used directly:

- `run(query: str, artifacts: list[TextArtifact])` reranks a list of [TextArtifact](../../reference/griptape/artifacts/text_artifact.md) based on the original query.

Rerank Drivers can also be used with a [RagEngine's Rerank Module](../engines/rag-engines.md#retrieval-stage-modules).

## Rerank Drivers

### Local

The [LocalRerankDriver](../../reference/griptape/drivers/rerank/local_rerank_driver.md) uses a simple relatedness calculation.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/drivers/src/local_rerank_driver.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/drivers/logs/local_rerank_driver.txt"
    ```

### Cohere

The [CohereRerankDriver](../../reference/griptape/drivers/rerank/cohere_rerank_driver.md) uses [Cohere's Rerank](https://cohere.com/rerank) model.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/drivers/src/cohere_rerank_driver.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/drivers/logs/cohere_rerank_driver.txt"
    ```

### Nvidia NIM

The [NvidiaNimRerankDriver](../../reference/griptape/drivers/rerank/nvidia_nim_rerank_driver.md) uses the [Nvidia NIM Reranking API](https://docs.nvidia.com/nim/nemo-retriever/text-reranking/latest/index.html).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/drivers/src/nvidia_nim_rerank_driver.py"
    ```
