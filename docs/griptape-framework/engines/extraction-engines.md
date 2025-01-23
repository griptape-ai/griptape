______________________________________________________________________

## search: boost: 2

## Overview

Extraction Engines enable the extraction of structured data from unstructured text.
These Engines can be used with Structures via [Extraction Tasks](../../griptape-framework/structures/tasks.md).
As of now, Griptape supports two types of Extraction Engines: the CSV Extraction Engine and the JSON Extraction Engine.

## CSV

The CSV Extraction Engine extracts comma separated values from unstructured text.

```python
--8<-- "docs/griptape-framework/engines/src/extraction_engines_1.py"
```

```
name,age,location
Alice,28,New York
Bob,35,California
Charlie,40,
Collin,28,San Francisco
```

## JSON

The JSON Extraction Engine extracts JSON-formatted values from unstructured text.

```python
--8<-- "docs/griptape-framework/engines/src/extraction_engines_2.py"
```

```
{
  "model": "GPT-3.5",
  "notes": [
    "Part of OpenAI's GPT series.",
    "Used in ChatGPT and Microsoft Copilot."
  ]
}
{
  "model": "GPT-4",
  "notes": [
    "Part of OpenAI's GPT series.",
    "Praised for increased accuracy and multimodal capabilities.",
    "Architecture and number of parameters not revealed."
  ]
}
...Output truncated for brevity...
```
