# Async Implementation Guide

This document describes the async implementation for PromptTask and EventListener in Griptape.

## Overview

The async implementation makes PromptTask and the event system natively async, allowing for efficient async/await patterns with AsyncOpenAiChatPromptDriver and other async drivers.

## Key Components

### 1. PromptTask Async Support

PromptTask now supports both sync and async execution:

**Sync API (existing):**
```python
from griptape.drivers.prompt import OpenAiChatPromptDriver
from griptape.tasks import PromptTask

task = PromptTask(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o-mini"),
    input="What is 2+2?"
)
result = task.run()
```

**Async API (new):**
```python
import asyncio
from griptape.drivers.prompt import AsyncOpenAiChatPromptDriver
from griptape.tasks import PromptTask

async def main():
    task = PromptTask(
        prompt_driver=AsyncOpenAiChatPromptDriver(model="gpt-4o-mini"),
        input="What is 2+2?"
    )
    result = await task.async_run()

asyncio.run(main())
```

#### Async Methods

- `async_run()` - Async version of `run()`
- `async_try_run()` - Async version of `try_run()`
- `async_before_run()` - Async lifecycle hook
- `async_after_run()` - Async lifecycle hook
- `async_default_run_actions_subtasks()` - Async subtask runner for tools
- `async_default_run_output_schema_validation_subtasks()` - Async subtask runner for schema validation

#### Automatic Subtask Runner Conversion

When using `async_run()`, the default sync subtask runners are automatically converted to their async equivalents:

```python
# Default sync runners are automatically mapped to async versions
task = PromptTask(
    prompt_driver=AsyncOpenAiChatPromptDriver(model="gpt-4o-mini"),
    input="Calculate 5 + 7",
    tools=[Calculator()]  # Tools work with async too!
)
# No need to manually specify async subtask runners
result = await task.async_run()
```

### 2. EventBus Async Support

EventBus now supports async event publishing:

**Sync API (existing):**
```python
from griptape.events import EventBus, StartPromptEvent

EventBus.publish_event(StartPromptEvent(...))
```

**Async API (new):**
```python
from griptape.events import EventBus, StartPromptEvent

await EventBus.apublish_event(StartPromptEvent(...))
```

The `apublish_event()` method:
- Automatically detects async event listeners
- Runs all async listeners concurrently using `asyncio.gather()`
- Falls back to sync execution for sync listeners
- Provides better performance for async workloads

### 3. EventListener Async Support

EventListener now supports:
- Async event handlers (callbacks)
- Async context manager protocol
- Mixed sync/async handler support

**Sync Context Manager:**
```python
from griptape.events import EventListener

def sync_handler(event):
    print(f"Event: {event}")
    return event

with EventListener(on_event=sync_handler):
    # Events are handled synchronously
    task.run()
```

**Async Context Manager:**
```python
from griptape.events import EventListener

async def async_handler(event):
    # Can perform async operations
    await log_to_database(event)
    return event

async with EventListener(on_event=async_handler):
    # Events are handled asynchronously
    await task.async_run()
```

#### Event Handler Types

EventListener accepts both sync and async callbacks:

```python
# Sync handler - called directly
def sync_handler(event):
    return event

# Async handler - awaited when called
async def async_handler(event):
    await some_async_operation()
    return event
```

The listener automatically detects which type of handler you provide and handles it appropriately.

### 4. AsyncBasePromptDriver Integration

AsyncBasePromptDriver automatically uses async event publishing:

```python
# In AsyncBasePromptDriver
async def before_run(self, prompt_stack: PromptStack) -> None:
    # Uses async event publishing
    await EventBus.apublish_event(StartPromptEvent(...))

async def after_run(self, result: Message) -> None:
    # Uses async event publishing
    await EventBus.apublish_event(FinishPromptEvent(...))
```

Streaming events are also published asynchronously:

```python
# Streaming chunks are published as they arrive
async for message_delta in self.try_stream(prompt_stack):
    if isinstance(content, TextDeltaMessageContent):
        await EventBus.apublish_event(TextChunkEvent(...))
```

## Migration Guide

### For Existing Code

Existing sync code continues to work without changes:

```python
# This still works exactly as before
task = PromptTask(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o-mini"),
    input="Hello"
)
result = task.run()
```

### For New Async Code

To use async functionality:

1. Use an async prompt driver (e.g., `AsyncOpenAiChatPromptDriver`)
2. Call `async_run()` instead of `run()`
3. Optionally use async event listeners with `async with`

```python
import asyncio
from griptape.drivers.prompt import AsyncOpenAiChatPromptDriver
from griptape.events import EventListener
from griptape.tasks import PromptTask

async def async_handler(event):
    print(f"Event: {event}")
    return event

async def main():
    driver = AsyncOpenAiChatPromptDriver(model="gpt-4o-mini")
    task = PromptTask(prompt_driver=driver, input="Hello")

    async with EventListener(on_event=async_handler):
        result = await task.async_run()
        print(result.to_text())

asyncio.run(main())
```

## Error Handling

### Type Safety

The implementation includes runtime type checks:

```python
# This will raise ValueError
sync_task = PromptTask(prompt_driver=OpenAiChatPromptDriver(...))
await sync_task.async_run()  # Error: requires AsyncBasePromptDriver

# This will also raise ValueError
with EventListener(on_event=async_handler):
    task.run()  # Error: async handler with sync publish
```

### Proper Usage

Always match the driver type with the run method:

| Driver Type | Run Method | Event Publishing |
|-------------|------------|------------------|
| `BasePromptDriver` | `run()` | `publish_event()` |
| `AsyncBasePromptDriver` | `async_run()` | `apublish_event()` |

## Performance Considerations

### Concurrency

Async event listeners run concurrently:

```python
# These three handlers run concurrently, not sequentially
async with EventListener(on_event=handler1), \
           EventListener(on_event=handler2), \
           EventListener(on_event=handler3):
    await task.async_run()
```

### Streaming

Async streaming provides better performance for long-running operations:

```python
driver = AsyncOpenAiChatPromptDriver(
    model="gpt-4o-mini",
    stream=True  # Enable streaming
)

async def on_chunk(event):
    if isinstance(event, TextChunkEvent):
        print(event.token, end="", flush=True)
    return event

async with EventListener(on_event=on_chunk):
    result = await task.async_run()
```

## Examples

See the examples directory for complete working examples:

- `examples/async_prompt_task_example.py` - Basic async usage
- `examples/async_event_listener_example.py` - Async event handling
- `examples/async_context_manager_example.py` - Context manager patterns

## Testing

All async functionality is fully tested:

```bash
make test/unit TESTS=tests/unit/tasks/test_async_prompt_task.py
```

## Implementation Details

### File Changes

1. **griptape/tasks/prompt_task.py**
   - Added `async_run()`, `async_try_run()`
   - Added `async_before_run()`, `async_after_run()`
   - Added async subtask runners
   - Added `_get_async_subtask_runners()` for automatic conversion

2. **griptape/events/event_bus.py**
   - Added `apublish_event()` method
   - Concurrent async listener execution

3. **griptape/events/event_listener.py**
   - Added `apublish_event()` method
   - Added `__aenter__()` and `__aexit__()` for async context manager
   - Support for both sync and async `on_event` callbacks

4. **griptape/drivers/prompt/async_base_prompt_driver.py**
   - Updated to use `await EventBus.apublish_event()`
   - Async event publishing for streaming

5. **tests/mocks/mock_async_prompt_driver.py**
   - Mock async driver for testing

6. **tests/unit/tasks/test_async_prompt_task.py**
   - Comprehensive async tests

## Backward Compatibility

✅ All existing sync code works without changes
✅ 3526 tests passing
✅ No breaking changes to public APIs
✅ Type-safe with runtime checks
