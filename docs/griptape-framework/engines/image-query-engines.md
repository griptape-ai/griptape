---
search:
  boost: 2 
---

## Image Query Engines

The [Image Query Engine](../../reference/griptape/engines/image_query/image_query_engine.md) allows you to perform natural language queries on the contents of images. You can specify the provider and model used to query the image by providing the Engine with a particular [Image Query Driver](../drivers/image-query-drivers.md).

All Image Query Drivers default to a `max_tokens` of 256. You can tune this value based on your use case and the [Image Query Driver](../drivers/image-query-drivers.md) you are providing.

```python
--8<-- "docs/griptape-framework/engines/src/image_query_engines_1.py"
```
