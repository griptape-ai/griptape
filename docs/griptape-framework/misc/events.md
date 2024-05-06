## Overview

You can use [EventListener](../../reference/griptape/events/event_listener.md)s to listen for events during a Structure's execution.
See [Event Listener Drivers](../drivers/event-listener-drivers.md) for examples on forwarding events to external services.

## Specific Event Types

You can listen to specific event types:

```python
from griptape.structures import Agent
from griptape.events import (
    BaseEvent,
    StartTaskEvent,
    FinishTaskEvent,
    StartActionsSubtaskEvent,
    FinishActionsSubtaskEvent,
    StartPromptEvent,
    FinishPromptEvent,
    EventListener,
)


def handler(event: BaseEvent):
    print(event.__class__)


agent = Agent(
    event_listeners=[
        EventListener(
            handler,
            event_types=[
                StartTaskEvent,
                FinishTaskEvent,
                StartActionsSubtaskEvent,
                FinishActionsSubtaskEvent,
                StartPromptEvent,
                FinishPromptEvent,
            ],
        )
    ]
)

agent.run("tell me about griptape")
```
```
<class 'griptape.events.start_task_event.StartTaskEvent'>
[09/08/23 10:51:16] INFO     PromptTask a20c236d1d86480fb14ae976e6cf8983
                             Input: tell me about griptape
<class 'griptape.events.start_prompt_event.StartPromptEvent'>
<class 'griptape.events.finish_prompt_event.FinishPromptEvent'>
[09/08/23 10:51:27] INFO     PromptTask a20c236d1d86480fb14ae976e6cf8983
                             Output: Griptape is a gritty, sandpaper-like material that is applied to the top of a skateboard deck. It
                             provides traction and grip, allowing skateboarders to keep their feet firmly on the board and perform tricks more
                             easily. Griptape comes in different colors and designs, but the most common type is black. It's adhesive on one
                             side so it can stick to the skateboard. Over time, griptape can wear down and need to be replaced to maintain
                             optimal performance. It's an essential component for skateboarding and other similar sports.
<class 'griptape.events.finish_task_event.FinishTaskEvent'>
```

## All Event Types

Or listen to all events:

```python
from griptape.structures import Agent
from griptape.events import BaseEvent, EventListener


def handler1(event: BaseEvent):
    print("Handler 1", event.__class__)


def handler2(event: BaseEvent):
    print("Handler 2", event.__class__)


agent = Agent(
    event_listeners=[
        EventListener(handler1),
        EventListener(handler2),
    ]
)

agent.run("tell me about griptape")
```

```
Handler 1 <class 'griptape.events.start_structure_run_event.StartStructureRunEvent'>
Handler 2 <class 'griptape.events.start_structure_run_event.StartStructureRunEvent'>
Handler 1 <class 'griptape.events.start_task_event.StartTaskEvent'>
Handler 2 <class 'griptape.events.start_task_event.StartTaskEvent'>
[10/26/23 11:49:29] INFO     PromptTask 20e3ef1f8856453ebabc84863ac36784
                             Input: tell me about griptape
Handler 1 <class 'griptape.events.start_prompt_event.StartPromptEvent'>
Handler 2 <class 'griptape.events.start_prompt_event.StartPromptEvent'>
Handler 1 <class 'griptape.events.finish_prompt_event.FinishPromptEvent'>
Handler 2 <class 'griptape.events.finish_prompt_event.FinishPromptEvent'>
[10/26/23 11:49:55] INFO     PromptTask 20e3ef1f8856453ebabc84863ac36784
                             Output: Griptape is a gritty, sandpaper-like material that is applied to the top of
                             a skateboard, longboard, or scooter deck to provide traction between the rider's
                             feet and the deck. It is an essential component for performing tricks and
                             maintaining control of the board or scooter.

                             Griptape is typically black, but it comes in a variety of colors and designs. It is
                             made by embedding an abrasive material (similar to sand) into a tough,
                             weather-resistant adhesive. The adhesive side is then applied to the deck, while
                             the abrasive side faces up to provide grip.

                             The grip provided by the griptape allows riders to keep their footing on the board,
                             especially during tricks where the board is flipped or spun. It also helps riders
                             control the board better during downhill rides or sharp turns.

                             Over time, griptape can wear down and lose its effectiveness, at which point it can
                             be removed and replaced. It's an essential part of skateboarding equipment and
                             plays a significant role in the sport's safety and performance.
Handler 1 <class 'griptape.events.finish_task_event.FinishTaskEvent'>
Handler 2 <class 'griptape.events.finish_task_event.FinishTaskEvent'>
Handler 1 <class 'griptape.events.finish_structure_run_event.FinishStructureRunEvent'>
Handler 2 <class 'griptape.events.finish_structure_run_event.FinishStructureRunEvent'>
```

## Streaming


You can use the [CompletionChunkEvent](../../reference/griptape/events/completion_chunk_event.md) to stream the completion results from Prompt Drivers.

```python
from griptape.events import CompletionChunkEvent, EventListener
from griptape.tasks import ToolkitTask
from griptape.structures import Pipeline
from griptape.tools import WebScraper, TaskMemoryClient


pipeline = Pipeline(
    event_listeners=[
        EventListener(
            lambda e: print(e.token, end="", flush=True),
            event_types=[CompletionChunkEvent],
        )
    ]
)

pipeline.add_tasks(
    ToolkitTask(
        "Based on https://griptape.ai, tell me what griptape is.",
        tools=[WebScraper(), TaskMemoryClient(off_prompt=False)],
    )
)

pipeline.run()
```

You can also use the [Stream](../../reference/griptape/utils/stream.md) utility to automatically wrap
[CompletionChunkEvent](../../reference/griptape/events/completion_chunk_event.md)s in a Python iterator.

```python
from griptape.utils import Stream
from griptape.tasks import ToolkitTask
from griptape.structures import Pipeline
from griptape.tools import WebScraper


pipeline = Pipeline()
pipeline.config.global_drivers.prompt_driver.stream = True
pipeline.add_tasks(ToolkitTask("Based on https://griptape.ai, tell me what griptape is.", tools=[WebScraper()]))

for artifact in Stream(pipeline).run():
    print(artifact.value, end="", flush=True),
```


## Counting Tokens

To count tokens, you can use Event Listeners and the [TokenCounter](../../reference/griptape/utils/token_counter.md) util:

```python
from griptape import utils
from griptape.events import BaseEvent, StartPromptEvent, FinishPromptEvent, EventListener
from griptape.structures import Agent


token_counter = utils.TokenCounter()


def count_tokens(e: BaseEvent):
    if isinstance(e, StartPromptEvent) or isinstance(e, FinishPromptEvent):
        token_counter.add_tokens(e.token_count)


agent = Agent(
    event_listeners=[
        EventListener(
            handler=lambda e: count_tokens(e),
            event_types=[StartPromptEvent, FinishPromptEvent],
        )
    ]
)

agent.run("tell me about large language models")

print(f"total tokens: {token_counter.tokens}")
```

```
[09/25/23 16:32:41] INFO     PromptTask c93569eb1d264675b52bef184b269621
                             Input: tell me about large language models
[09/25/23 16:33:01] INFO     PromptTask c93569eb1d264675b52bef184b269621
                             Output: Large language models are a type of artificial intelligence model that are trained on
                             a vast amount of text data. They are designed to generate human-like text based on the input
                             they are given. These models can answer questions, write essays, summarize texts, translate
                             languages, and even generate creative content like poetry or stories.

                             One of the most well-known large language models is GPT-3, developed by OpenAI. It has 175
                             billion machine learning parameters and was trained on hundreds of gigabytes of text.

                             These models work by predicting the probability of a word given the previous words used in
                             the text. They don't understand text in the way humans do, but they can generate coherent and
                             contextually relevant sentences by learning patterns in the data they were trained on.

                             However, they also have limitations. For instance, they can sometimes generate incorrect or
                             nonsensical responses. They can also be sensitive to slight changes in input phrasing, and
                             they don't have the ability to fact-check information or access real-time data, so they can't
                             provide up-to-date information or verify the truthfulness of their outputs. They also don't
                             have a sense of ethics or morality, so they rely on guidelines and safety measures put in
                             place by their developers.
total tokens: 273
```


## Inspecting Payloads

You can use the [StartPromptEvent](../../reference/griptape/events/start_prompt_event.md) to inspect the Prompt Stack and final prompt string before it is sent to the LLM. 

```python
from griptape.structures import Agent
from griptape.events import BaseEvent, StartPromptEvent, EventListener


def handler(event: BaseEvent):
    if isinstance(event, StartPromptEvent):
        print("Prompt Stack Inputs:")
        for input in event.prompt_stack.inputs:
            print(f"{input.role}: {input.content}")
        print("Final Prompt String:")
        print(event.prompt)


agent = Agent(
    event_listeners=[EventListener(handler=handler, event_types=[StartPromptEvent])]
)

agent.run("Write me a poem.")
```
```
...
Prompt Stack Inputs:
system:
user: Write me a poem.
Final Prompt String:


User: Write me a poem.

Assistant:
...
```
