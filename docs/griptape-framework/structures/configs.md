---
search:
  boost: 2
---

## Overview

Griptape exposes a global singleton, [Defaults](../../reference/griptape/configs/defaults_config.md), which can be used to access and modify the default configurations of the framework.

To update the default configurations, simply update the fields on the `Defaults` object.
Framework objects will be created with the currently set default configurations, but you can always override at the individual class level.

### Loading/Saving Configs

You can serialize and deserialize Driver Configs using the [to_json()](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin.to_json) and [from_json()](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin.from_json) methods.

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_8.py"
```
