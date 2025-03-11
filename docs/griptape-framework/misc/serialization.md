---
search:
  boost: 2
---

## Overview

Many components in Griptape can be serialized and deserialized using the [to_dict](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin.to_dict) and [from_dict](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin.from_dict) methods.
There are also [to_json](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin.to_json) and [from_json](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin.from_json) as a convenience.

Here is how we can serialize an `Agent` and then deserialize it back:

```python
--8<-- "docs/griptape-framework/misc/src/serialization_1.py"
```

## Serialization Overrides

All classes that implement the [SerializableMixin](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin) can be serialized using the above methods.
However, only fields marked with `metadata={"serializable": True}` will be included in the serialization process.
If you need to add or remove fields in the serialization process, you can pass [serialization_overrides](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin.serialization_overrides) to any of the serialization methods.

```python
--8<-- "docs/griptape-framework/misc/src/serialization_2.py"
```

## Types Overrides

Due to some unfortunate internals of the Griptape's serialization process, you may occasionally run into a `NameError` when serializing. It will look something like this:

```text
NameError: name 'BaseWebSearchDriver' is not defined
```

This is something we're [actively working](https://github.com/griptape-ai/griptape/issues/1587) on fixing, but in the meantime, you can use the [types_overrides](../../reference/griptape/mixins/serializable_mixin.md#griptape.mixins.serializable_mixin.SerializableMixin.types_overrides) parameter to pass in a dictionary of types that need to be overridden during serialization.

Here is an example of how you can use `types_overrides`:

```python
--8<-- "docs/griptape-framework/misc/src/serialization_3.py"
```
