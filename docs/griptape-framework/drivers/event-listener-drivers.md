---
search:
  boost: 2 
---

## Overview

Event Listener Drivers are used to send Griptape [Events](../misc/events.md) to external services.

You can instantiate Drivers and pass them to Event Listeners in your Structure:

```python
--8<-- "docs/griptape-framework/drivers/src/event_listener_drivers_1.py"
```

Or use them independently:

```python
--8<-- "docs/griptape-framework/drivers/src/event_listener_drivers_2.py"
```

## Event Listener Drivers

Griptape offers the following Event Listener Drivers for forwarding Griptape Events.

### Amazon SQS

!!! info
    This driver requires the `drivers-event-listener-amazon-sqs` [extra](../index.md#extras).

The [AmazonSqsEventListenerDriver](../../reference/griptape/drivers/event_listener/amazon_sqs_event_listener_driver.md) sends Events to an [Amazon SQS](https://aws.amazon.com/sqs/) queue.

```python
--8<-- "docs/griptape-framework/drivers/src/event_listener_drivers_3.py"
```

### AWS IoT

!!! info
    This driver requires the `drivers-event-listener-amazon-iot` [extra](../index.md#extras).

The [AwsIotCoreEventListenerDriver](../../reference/griptape/drivers/event_listener/aws_iot_core_event_listener_driver.md) sends Events to the [AWS IoT Message Broker](https://aws.amazon.com/iot-core/).

```python
--8<-- "docs/griptape-framework/drivers/src/event_listener_drivers_4.py"
```

### Griptape Cloud

The [GriptapeCloudEventListenerDriver](../../reference/griptape/drivers/event_listener/griptape_cloud_event_listener_driver.md) sends Events to [Griptape Cloud](https://www.griptape.ai/cloud).

!!! note
    This Driver is required when using the Griptape Cloud Managed Structures feature. For local development, you can use the [Skatepark Emulator](https://github.com/griptape-ai/griptape-cli?tab=readme-ov-file#skatepark-emulator).

```python
--8<-- "docs/griptape-framework/drivers/src/event_listener_drivers_5.py"
``` 

### Webhook Event Listener Driver

The [WebhookEventListenerDriver](../../reference/griptape/drivers/event_listener/webhook_event_listener_driver.md) sends Events to any [Webhook](https://en.wikipedia.org/wiki/Webhook) URL.

```python
--8<-- "docs/griptape-framework/drivers/src/event_listener_drivers_6.py"
```
### Pusher

!!! info
    This driver requires the `drivers-event-listener-pusher` [extra](../index.md#extras).

The [PusherEventListenerDriver](../../reference/griptape/drivers/event_listener/pusher_event_listener_driver.md) sends Events to [Pusher](https://pusher.com).

```python
--8<-- "docs/griptape-framework/drivers/src/event_listener_drivers_7.py"
```
