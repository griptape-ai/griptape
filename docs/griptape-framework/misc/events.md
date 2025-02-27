---
search:
  boost: 2
---

## Overview

You can configure the global [EventBus](../../reference/griptape/events/event_bus.md) with [EventListener](../../reference/griptape/events/event_listener.md)s to listen for various framework events.
See [Event Listener Drivers](../drivers/event-listener-drivers.md) for examples on forwarding events to external services.

## Specific Event Types

You can listen to specific event types:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_1.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_1.txt"
    ```

## All Event Types

Or listen to all events:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_2.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_2.txt"
    ```

## Stream Iterator

You can use `Structure.run_stream()` for streaming Events from the `Structure` in the form of an iterator.

!!! tip

    Set `stream=True` on your [Prompt Driver](../drivers/prompt-drivers.md) in order to receive completion chunk events.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_streaming.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_streaming.txt"
    ```

## Context Managers

You can also use [EventListener](../../reference/griptape/events/event_listener.md)s as a Python Context Manager.
The `EventListener` will automatically be added and removed from the [EventBus](../../reference/griptape/events/event_bus.md) when entering and exiting the context.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_context.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_context.txt"
    ```

## Streaming

You can use the [BaseChunkEvent](../../reference/griptape/events/base_chunk_event.md) to stream the completion results from Prompt Drivers.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_3.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_3.txt"
    ```

You can also use the [TextChunkEvent](../../reference/griptape/events/text_chunk_event.md) and [ActionChunkEvent](../../reference/griptape/events/action_chunk_event.md) to further differentiate the different types of chunks for more customized output.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_chunk_stream.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_chunk_stream.txt"
    ```

If you want Griptape to handle the chunk events for you, use the [Stream](../../reference/griptape/utils/stream.md) utility to automatically wrap
[BaseChunkEvent](../../reference/griptape/events/base_chunk_event.md)s in a Python iterator.

The `Stream` utility does not automatically enable streaming on the Drivers that produce `BaseChunkEvent`s.
Make sure to enable streaming on the Drivers or else `Stream` will yield no iterations.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_4.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_4.txt"
    ```

## Counting Tokens

To count tokens, you can use Event Listeners and the [TokenCounter](../../reference/griptape/utils/token_counter.md) util:

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_5.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_5.txt"
    ```

## Inspecting Payloads

You can use the [StartPromptEvent](../../reference/griptape/events/start_prompt_event.md) to inspect the Prompt Stack and final prompt string before it is sent to the LLM.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_6.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_6.txt"
    ```

```
...
Prompt Stack Messages:
system:
user: Write me a poem.
Final Prompt String:


User: Write me a poem.

Assistant:
...
```

## `EventListenerDriver.on_event` Return Value Behavior

The value that gets returned from the [`EventListener.on_event`](../../reference/griptape/events/event_listener.md#griptape.events.event_listener.EventListener.on_event) will determine what gets sent to the `event_listener_driver`.

### `EventListener.on_event` is None

By default, the `EventListener.on_event` function is `None`. Any events that the `EventListener` is listening for will get sent to the `event_listener_driver` as-is.

### Return `BaseEvent` or `dict`

You can return a `BaseEvent` or `dict` object from `EventListener.on_event`, and it will get sent to the `event_listener_driver`.

### Return `None`

You can return `None` in the on_event function to prevent the event from getting sent to the `event_listener_driver`.

=== "Code"

    ```python
    --8<-- "docs/griptape-framework/misc/src/events_no_publish.py"
    ```

=== "Logs"

    ```text
    --8<-- "docs/griptape-framework/misc/logs/events_no_publish.txt"
    ```
