---
search:
  boost: 2
---

## Overview

Griptape provides a set of official Tools for common tasks. In general, Griptape-included Tools are designed to be general-purpose and Driver-based for easy integration with different backends.

## Tools

### Audio Transcription

This Tool enables [Agents](../../../griptape-framework/structures/agents.md) to transcribe speech from text using [Audio Transcription Drivers](../../../reference/griptape/drivers/audio_transcription/base_audio_transcription_driver.md).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/audio_transcription_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/audio_transcription_tool_1.txt"
    ```

### Calculator

This tool enables LLMs to make simple calculations.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/calculator_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/calculator_tool_1.txt"
    ```

### Computer

This tool enables LLMs to execute Python code and run shell commands inside a Docker container. You have to have the Docker daemon running in order for this tool to work.

You can specify a local working directory and environment variables during tool initialization:

```python
--8<-- "docs/griptape-framework/tools/official-tools/src/computer_tool_1.py"
```

### Date Time

This tool enables LLMs to get current date and time.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/date_time_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/date_time_tool_1.txt"
    ```

### Email

The [EmailTool](../../../reference/griptape/tools/email/tool.md) enables LLMs to send emails.

```python
--8<-- "docs/griptape-framework/tools/official-tools/src/email_tool_1.py"
```

For debugging purposes, you can run a local SMTP server that the LLM can send emails to:

```shell
python -m smtpd -c DebuggingServer -n localhost:1025
```

### Extraction

The [ExractionTool](../../../reference/griptape/tools/extraction/tool.md) enables LLMs to extract structured text from unstructured data.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/extraction_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/extraction_tool_1.txt"
    ```

### File Manager

This tool enables LLMs to save and load files.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/file_manager_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/file_manager_tool_1.txt"
    ```

### Griptape Cloud Tool

The [GriptapeCloudToolTool](../../../reference/griptape/tools/griptape_cloud_tool/tool.md) integrates with Griptape Cloud's hosted Tools.

**Note:** This tool requires a [Tool](https://cloud.griptape.ai/tools) hosted in Griptape Cloud and an [API Key](https://cloud.griptape.ai/configuration/api-keys) for access.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/griptape_cloud_tool_tool.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/griptape_cloud_tool_tool.txt"
    ```

### Image Query

This tool allows Agents to execute natural language queries on the contents of images using multimodal models.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/image_query_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/image_query_tool_1.txt"
    ```

### Inpainting Image Generation

This tool allows LLMs to generate images using inpainting, where an input image is altered within the area specified by a mask image according to a prompt. The input and mask images can be provided either by their file path or by their [Task Memory](../../../griptape-framework/structures/task-memory.md) references.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/inpainting_image_generation_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/inpainting_image_generation_tool_1.txt"
    ```

### MCP

This tool allows LLMs to call MCP Tools. It requires [MCP](https://github.com/modelcontextprotocol/python-sdk) and Python 3.10 or greater.

### Outpainting Image Generation

This tool allows LLMs to generate images using outpainting, where an input image is altered outside of the area specified by a mask image according to a prompt. The input and mask images can be provided either by their file path or by their [Task Memory](../../../griptape-framework/structures/task-memory.md) references.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/outpainting_image_generation_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/outpainting_image_generation_tool_1.txt"
    ```

### Prompt Image Generation

This tool allows LLMs to generate images from a text prompt.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/prompt_image_generation_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/prompt_image_generation_tool_1.txt"
    ```

### Prompt Summary

The [PromptSummaryTool](../../../reference/griptape/tools/prompt_summary/tool.md) enables LLMs summarize text data.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/prompt_summary_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/prompt_summary_tool_1.txt"
    ```

### Rag

The [RagTool](../../../reference/griptape/tools/rag/tool.md) enables LLMs to query modular RAG engines.

Here is an example of how it can be used with a local vector store driver:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/rag_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/rag_tool_1.txt"
    ```

### Query

The [QueryTool](../../../reference/griptape/tools/query/tool.md) enables Agents to query unstructured data for specific information.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/query_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/query_tool_1.txt"
    ```

### Rest Api

This tool enables LLMs to call REST APIs.

The [RestApiTool](../../../reference/griptape/tools/rest_api/tool.md) tool uses the following parameters:

The following example is built using [https://jsonplaceholder.typicode.com/guide/](https://jsonplaceholder.typicode.com/guide/).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/rest_api_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/rest_api_tool_1.txt"
    ```

### Sql

This tool enables LLMs to execute SQL statements via [SQLAlchemy](https://www.sqlalchemy.org/). Depending on your underlying SQL engine, [configure](https://docs.sqlalchemy.org/en/20/core/engines.html) your `engine_url` and give the LLM a hint about what engine you are using via `engine_name`, so that it can create engine-specific statements.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/sql_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/sql_tool_1.txt"
    ```

### Structure Run

The [StructureRunTool](../../../reference/griptape/tools/structure_run/tool.md) Tool provides a way to run Structures via a Tool.
It requires you to provide a [Structure Run Driver](../../../griptape-framework/drivers/structure-run-drivers.md) to run the Structure in the desired environment.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/structure_run_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/structure_run_tool_1.txt"
    ```

### Text To Speech

This Tool enables LLMs to synthesize speech from text using [Text to Speech Drivers](../../../reference/griptape/drivers/text_to_speech/index.md).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/text_to_speech_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/text_to_speech_tool_1.txt"
    ```

### Variation Image Generation

This Tool allows LLMs to generate variations of an input image from a text prompt. The input image can be provided either by its file path or by its [Task Memory](../../../griptape-framework/structures/task-memory.md) reference.

#### Referencing an Image by File Path

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/variation_image_generation_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/variation_image_generation_tool_1.txt"
    ```

#### Referencing an Image in Task Memory

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/variation_image_generation_tool_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/variation_image_generation_tool_2.txt"
    ```

### Vector Store

The [VectorStoreTool](../../../reference/griptape/tools/vector_store/tool.md) enables LLMs to query vector stores.

Here is an example of how it can be used with a local vector store driver:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/vector_store_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/vector_store_tool_1.txt"
    ```

### Web Scraper

This tool enables LLMs to scrape web pages for full text, summaries, authors, titles, and keywords. It can also execute search queries to answer specific questions about the page. This tool uses OpenAI APIs for some of its activities, so in order to use it provide a valid API key in `openai_api_key`.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/web_scraper_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/web_scraper_tool_1.txt"
    ```

### Web Search

This tool enables LLMs to search the web.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/web_search_tool_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/web_search_tool_1.txt"
    ```

Extra schema properties can be added to the Tool to allow for more customization if the Driver supports it.
In this example, we add a `sort` property to the `search` Activity which will be added as a [Google custom search query parameter](https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list).

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/tools/official-tools/src/web_search_tool_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/tools/official-tools/logs/web_search_tool_2.txt"
    ```
