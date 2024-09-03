# Migration Guide

This document provides instructions for migrating your codebase to accommodate breaking changes introduced in new versions of Griptape.

## 0.30.X to 0.31.X

### Exceptions Over `ErrorArtifact`s

Drivers, Loaders, and Engines now raise exceptions rather than returning `ErrorArtifact`s.
Update any logic that expects `ErrorArtifact` to handle exceptions instead.

#### Before
```python
artifacts = WebLoader().load("https://www.griptape.ai")

if isinstance(artifacts, ErrorArtifact):
    raise Exception(artifacts.value)
```

#### After
```python
try:
    artifacts = WebLoader().load("https://www.griptape.ai")
except Exception as e:
    raise e
```

### LocalConversationMemoryDriver `file_path` renamed to `persist_file`

`LocalConversationMemoryDriver.file_path` has been renamed to `persist_file` and is now `Optional[str]`. If `persist_file` is not passed as a parameter, nothing will be persisted and no errors will be raised. `LocalConversationMemoryDriver` is now the default driver in the global `Defaults` object.

#### Before
```python
local_driver_with_file = LocalConversationMemoryDriver(
    file_path="my_file.json"
)

local_driver = LocalConversationMemoryDriver()

assert local_driver_with_file.file_path == "my_file.json"
assert local_driver.file_path == "griptape_memory.json"
```

#### After
```python
local_driver_with_file = LocalConversationMemoryDriver(
    persist_file="my_file.json"
)

local_driver = LocalConversationMemoryDriver()

assert local_driver_with_file.persist_file == "my_file.json"
assert local_driver.persist_file is None
```

### Changes to BaseConversationMemoryDriver

`BaseConversationMemoryDriver.driver` has been renamed to `conversation_memory_driver`. Method signatures for `.store` and `.load` have been changed.

#### Before
```python
memory_driver = LocalConversationMemoryDriver()

conversation_memory = ConversationMemory(
    driver=memory_driver
)

load_result: BaseConversationMemory = memory_driver.load()

memory_driver.store(conversation_memory)
```

#### After
```python
memory_driver = LocalConversationMemoryDriver()

conversation_memory = ConversationMemory(
    conversation_memory_driver=memory_driver
)

load_result: tuple[list[Run], dict[str, Any]] = memory_driver.load()

memory_driver.store(
    conversation_memory.runs,
    conversation_memory.meta
)
```
