## Overview

Event Listener Drivers are used to send Griptape [Events](../misc/events.md) to external services.

You can instantiate Drivers and pass them to Event Listeners in your Structure:

```python
import os

from griptape.drivers import AmazonSqsEventListenerDriver
from griptape.events import (
    EventListener,
)
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    rules=[
        Rule(
            value="You will be provided with a block of text, and your task is to extract a list of keywords from it."
        )
    ],
    event_listeners=[
        EventListener(
            handler=lambda event: {  # You can optionally use the handler to transform the event payload before sending it to the Driver
                "event": event.to_dict(),
            },
            driver=AmazonSqsEventListenerDriver(
                queue_url=os.environ["AMAZON_SQS_QUEUE_URL"],
            ),
        ),
    ],
)

agent.run(
    """Black-on-black ware is a 20th- and 21st-century pottery tradition developed by the Puebloan Native American ceramic artists in Northern New Mexico.
    Traditional reduction-fired blackware has been made for centuries by pueblo artists.
    Black-on-black ware of the past century is produced with a smooth surface, with the designs applied through selective burnishing or the application of refractory slip.
    Another style involves carving or incising designs and selectively polishing the raised areas.
    For generations several families from Kha'po Owingeh and P'ohwhóge Owingeh pueblos have been making black-on-black ware with the techniques passed down from matriarch potters. Artists from other pueblos have also produced black-on-black ware.
    Several contemporary artists have created works honoring the pottery of their ancestors."""
)
```

Or use them independently:

```python
import os
from griptape.drivers import GriptapeCloudEventListenerDriver
from griptape.events import FinishStructureRunEvent
from griptape.artifacts import TextArtifact

event_driver = GriptapeCloudEventListenerDriver(
    api_key=os.environ["GRIPTAPE_CLOUD_API_KEY"]
)

done_event = FinishStructureRunEvent(
    output_task_input=TextArtifact("Just started!"),
    output_task_output=TextArtifact("All done!"),
)

event_driver.publish_event(done_event)
```

## Event Listener Drivers

Griptape offers the following Event Listener Drivers for forwarding Griptape Events.

### Amazon SQS

!!! info
    This driver requires the `drivers-event-listener-amazon-sqs` [extra](../index.md#extras).

The [AmazonSqsEventListenerDriver](../../reference/griptape/drivers/event_listener/amazon_sqs_event_listener_driver.md) sends Events to an [Amazon SQS](https://aws.amazon.com/sqs/) queue.

```python
import os

from griptape.drivers import AmazonSqsEventListenerDriver
from griptape.events import (
    EventListener,
)
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    rules=[
        Rule(
            value="You will be provided with a block of text, and your task is to extract a list of keywords from it."
        )
    ],
    event_listeners=[
        EventListener(
            driver=AmazonSqsEventListenerDriver(
                queue_url=os.environ["AMAZON_SQS_QUEUE_URL"],
            ),
        ),
    ],
)

agent.run(
    """Black-on-black ware is a 20th- and 21st-century pottery tradition developed by the Puebloan Native American ceramic artists in Northern New Mexico.
    Traditional reduction-fired blackware has been made for centuries by pueblo artists.
    Black-on-black ware of the past century is produced with a smooth surface, with the designs applied through selective burnishing or the application of refractory slip.
    Another style involves carving or incising designs and selectively polishing the raised areas.
    For generations several families from Kha'po Owingeh and P'ohwhóge Owingeh pueblos have been making black-on-black ware with the techniques passed down from matriarch potters. Artists from other pueblos have also produced black-on-black ware.
    Several contemporary artists have created works honoring the pottery of their ancestors."""
)
```

### AWS IoT

!!! info
    This driver requires the `drivers-event-listener-amazon-iot` [extra](../index.md#extras).

The [AwsIotCoreEventListenerDriver](../../reference/griptape/drivers/event_listener/aws_iot_core_event_listener_driver.md) sends Events to the [AWS IoT Message Broker](https://aws.amazon.com/iot-core/).

```python
import os

from griptape.config import StructureConfig
from griptape.drivers import AwsIotCoreEventListenerDriver, OpenAiChatPromptDriver
from griptape.events import (
    EventListener,
    FinishStructureRunEvent,
)
from griptape.rules import Rule
from griptape.structures import Agent

agent = Agent(
    rules=[
        Rule(
            value="You will be provided with a text, and your task is to extract the airport codes from it."
        )
    ],
    config=StructureConfig(
        prompt_driver=OpenAiChatPromptDriver(
            model="gpt-3.5-turbo", temperature=0.7
        )
    ),
    event_listeners=[
        EventListener(
            event_types=[FinishStructureRunEvent],
            driver=AwsIotCoreEventListenerDriver(
                topic=os.environ["AWS_IOT_CORE_TOPIC"],
                iot_endpoint=os.environ["AWS_IOT_CORE_ENDPOINT"],
            ),
        ),
    ],
)

agent.run("I want to fly from Orlando to Boston")
```

### Griptape Cloud

The [GriptapeCloudEventListenerDriver](../../reference/griptape/drivers/event_listener/griptape_cloud_event_listener_driver.md) sends Events to [Griptape Cloud](https://www.griptape.ai/cloud).

!!! note
    This Driver is required when using the Griptape Cloud Managed Structures feature. For local development, you can use the [Skatepark Emulator](https://github.com/griptape-ai/griptape-cli?tab=readme-ov-file#skatepark-emulator).

```python
import os

from griptape.drivers import GriptapeCloudEventListenerDriver
from griptape.events import (
    EventListener,
    FinishStructureRunEvent,
)
from griptape.structures import Agent

agent = Agent(
    event_listeners=[
        EventListener(
            event_types=[FinishStructureRunEvent],
            driver=GriptapeCloudEventListenerDriver(
                api_key=os.environ["GRIPTAPE_CLOUD_API_KEY"],
            ),
        ),
    ],
)

agent.run(
    "Create a list of 8 questions for an interview with a science fiction author."
)
``` 

### Webhook Event Listener Driver

The [WebhookEventListenerDriver](../../reference/griptape/drivers/event_listener/webhook_event_listener_driver.md) sends Events to any [Webhook](https://en.wikipedia.org/wiki/Webhook) URL.

```python
import os

from griptape.drivers import WebhookEventListenerDriver
from griptape.events import (
    EventListener,
    FinishStructureRunEvent,
)
from griptape.structures import Agent

agent = Agent(
    event_listeners=[
        EventListener(
            event_types=[FinishStructureRunEvent],
            driver=WebhookEventListenerDriver(
                webhook_url=os.environ["WEBHOOK_URL"],
            ),
        ),
    ],
)

agent.run("Analyze the pros and cons of remote work vs. office work")
```
### Pusher

!!! info
    This driver requires the `drivers-event-listener-pusher` [extra](../index.md#extras).

The [PusherEventListenerDriver](../../reference/griptape/drivers/event_listener/pusher_event_listener_driver.md) sends Events to [Pusher](https://pusher.com).

```python
import os
from griptape.drivers import PusherEventListenerDriver
from griptape.events import (
    EventListener,
    FinishStructureRunEvent
)
from griptape.structures import Agent

agent = Agent(
    event_listeners=[
        EventListener(
            event_types=[FinishStructureRunEvent],
            driver=PusherEventListenerDriver(
                batched=False,
                app_id=os.environ["PUSHER_APP_ID"],
                key=os.environ["PUSHER_KEY"],
                secret=os.environ["PUSHER_SECRET"],
                cluster=os.environ["PUSHER_CLUSTER"],
                channel='my-channel',
                event_name='my-event'
            ),
        ),
    ],
)

agent.run("Analyze the pros and cons of remote work vs. office work")

```
