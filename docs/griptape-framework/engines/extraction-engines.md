---
search:
  boost: 2 
---

## Overview
Extraction Engines in Griptape facilitate the extraction of data from text formats such as CSV and JSON.
These engines play a crucial role in the functionality of [Extraction Tasks](../../griptape-framework/structures/tasks.md).
As of now, Griptape supports two types of Extraction Engines: the CSV Extraction Engine and the JSON Extraction Engine.

## CSV

The CSV Extraction Engine is designed specifically for extracting data from CSV-formatted content.

!!! info
    The CSV Extraction Engine requires the `column_names` parameter for specifying the columns to be extracted.

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

The JSON Extraction Engine is tailored for extracting data from JSON-formatted content. 

!!! info
    The JSON Extraction Engine requires the `template_schema` parameter for specifying the structure to be extracted.

```python
--8<-- "docs/griptape-framework/engines/src/extraction_engines_2.py"
```
```
{'name': 'Alice', 'age': 28, 'location': 'New York'}
{'name': 'Bob', 'age': 35, 'location': 'California'}
```
