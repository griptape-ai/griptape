---
search:
  boost: 2 
---

## Overview
Extraction Engines in Griptape facilitate the extraction of data from text formats such as CSV and JSON.
These engines play a crucial role in the functionality of [Extraction Tasks](../../griptape-framework/structures/tasks.md).
As of now, Griptape supports two types of Extraction Engines: the CSV Extraction Engine and the JSON Extraction Engine.

## CSV

The CSV Extraction Engine extracts tabular content from unstructured data.

```python
--8<-- "docs/griptape-framework/engines/src/extraction_engines_1.py"
```
```
name,age,location
Alice,28,New York
Bob,35,California
Charlie,40,Texas
```

## JSON

The JSON Extraction Engine extracts JSON-formatted content from unstructed data. 


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
