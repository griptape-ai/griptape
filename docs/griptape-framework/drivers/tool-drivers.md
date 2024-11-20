---
search:
  boost: 2
---

## Overview

Tool Drivers can be used to augment [Tools](../../griptape-tools/index.md) with additional functionality.

You can use Tool Drivers with Tools:

```python
--8<-- "docs/griptape-framework/drivers/src/tool_driver_1.py"
```

In this example, the `RandomNumberGeneratorTool`'s schema is loaded from Griptape Cloud. Additionally, when the `RandomNumberGeneratorTool` is executed, it is run in the Cloud rather than locally.

## Tool Drivers

### Griptape Cloud

The [GriptapeCloudToolDriver](../../reference/griptape/drivers/tool/griptape_cloud_tool_driver.md) uses Griptape Cloud's hosted Tools service to modify the Tool with the hosted Tool's schema and execution logic.

```python
--8<-- "docs/griptape-framework/drivers/src/griptape_cloud_tool_driver_1.py"
```

The Driver will only overwrite activities present in the hosted Tool, meaning you can mix and match local and hosted activities.

```python
--8<-- "docs/griptape-framework/drivers/src/griptape_cloud_tool_driver_2.py"
```
