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

### `ImageArtifact.format` is now required

`ImageArtifact.format` is now a required parameter. Update any code that does not provide a `format` parameter.

#### Before

```python
image_artifact = ImageArtifact(
    b"image_data"
)
```

#### After
```python
image_artifact = ImageArtifact(
    b"image_data",
    format="jpeg"
)
```

### Removed `CsvRowArtifact`

`CsvRowArtifact` has been removed. Use `TextArtifact` instead.

#### Before

```python
artifact = CsvRowArtifact({"name": "John", "age": 30})
print(artifact.value) # {"name": "John", "age": 30}
print(type(artifact.value)) # <class 'dict'>
```

#### After
```python
artifact = TextArtifact("name: John\nage: 30")
print(artifact.value) # name: John\nage: 30
print(type(artifact.value)) # <class 'str'>
```

If you require storing a dictionary as an Artifact, you can use `GenericArtifact` instead.

### `CsvLoader`, `DataframeLoader`, and `SqlLoader` return types 

`CsvLoader`, `DataframeLoader`, and `SqlLoader` now return a `list[TextArtifact]` instead of `list[CsvRowArtifact]`.

If you require a dictionary, set a custom `formatter_fn` and then parse the text to a dictionary. 

#### Before

```python
results = CsvLoader().load(Path("people.csv").read_text())

print(results[0].value) # {"name": "John", "age": 30}
print(type(results[0].value)) # <class 'dict'>
```

#### After
```python
results = CsvLoader().load(Path("people.csv").read_text())

print(results[0].value) # name: John\nAge: 30
print(type(results[0].value)) # <class 'str'>

# Customize formatter_fn
results = CsvLoader(formatter_fn=lambda x: json.dumps(x)).load(Path("people.csv").read_text())
print(results[0].value) # {"name": "John", "age": 30}
print(type(results[0].value)) # <class 'str'>

dict_results = [json.loads(result.value) for result in results]
print(dict_results[0]) # {"name": "John", "age": 30}
print(type(dict_results[0])) # <class 'dict'>
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
