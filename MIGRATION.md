# Migration Guide

This document provides instructions for migrating your codebase to accommodate breaking changes introduced in new versions of Griptape.
## 0.31.X to 0.32.X

### Removed `MediaArtifact`

`MediaArtifact` has been removed. Use `ImageArtifact` or `AudioArtifact` instead.

#### Before

```python
image_media = MediaArtifact(
    b"image_data",
    media_type="image",
    format="jpeg"
)

audio_media = MediaArtifact(
    b"audio_data",
    media_type="audio",
    format="wav"
)
``` 

#### After
```python
image_artifact = ImageArtifact(
    b"image_data",
    format="jpeg"
)

audio_artifact = AudioArtifact(
    b"audio_data",
    format="wav"
)
```

### Changed `CsvRowArtifact.value` from `dict` to `str`.

`CsvRowArtifact`'s `value` is now a `str` instead of a `dict`. Update any logic that expects `dict` to handle `str` instead.

#### Before

```python
artifact = CsvRowArtifact({"name": "John", "age": 30})
print(artifact.value) # {"name": "John", "age": 30}
print(type(artifact.value)) # <class 'dict'>
```

#### After
```python
artifact = CsvRowArtifact({"name": "John", "age": 30})
print(artifact.value) # name: John\nAge: 30
print(type(artifact.value)) # <class 'str'>
```

### Moved `ImageArtifact.prompt` and `ImageArtifact.model` to `ImageArtifact.meta`

`ImageArtifact.prompt` and `ImageArtifact.model` have been moved to `ImageArtifact.meta`.

#### Before

```python
image_artifact = ImageArtifact(
    b"image_data",
    format="jpeg",
    prompt="Generate an image of a cat",
    model="DALL-E"
)

print(image_artifact.prompt, image_artifact.model) # Generate an image of a cat, DALL-E
```

#### After
```python
image_artifact = ImageArtifact(
    b"image_data",
    format="jpeg",
    meta={"prompt": "Generate an image of a cat", "model": "DALL-E"}
)

print(image_artifact.meta["prompt"], image_artifact.meta["model"]) # Generate an image of a cat, DALL-E
```


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
