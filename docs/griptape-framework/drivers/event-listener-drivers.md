## Overview

Event Listener Drivers are used to send Griptape [Events](../misc/events.md) to external services.

You can instantiate Drivers and pass them to Event Listeners in your Structure:

```python
```

Or use them independently:

```python
```

## Event Listener Drivers

Griptape offers the following Event Listener Drivers for forwarding Gritpape Events.

### Amazon SQS Event Listener Driver

!!! info
    This driver requires the `drivers-event-listener-amazon-sqs` [extra](../index.md#extras).

The [AmazonSqsEventListenerDriver](../../reference/griptape/drivers/event_listener/amazon_sqs_event_listener_driver) sends Events to an [Amazon SQS](https://aws.amazon.com/sqs/) queue.

```python
```

### AWS IoT Event Listener Driver

!!! info
    This driver requires the `drivers-event-listener-amazon-iot` [extra](../index.md#extras).

The [AwsIotCoreEventListenerDriver](../../reference/griptape/drivers/event_listener/aws_iot_core_event_listener_driver.md) sends Events to the [AWS IoT Message Broker](https://aws.amazon.com/iot-core/).

```python
```

### Griptape Cloud Event Listener Driver

The [GriptapeCloudEventListenerDriver](../../reference/griptape/drivers/event_listener/griptape_cloud_event_listener_driver.md) sends Events to [Griptape Cloud](https://www.griptape.ai/cloud).
This Driver is required when using the Griptape Cloud Managed Structures feature.

```python
``` 

### Webhook Event Listener Driver

The [WebhookEventListenerDriver](../../reference/griptape/drivers/event_listener/webhook_event_listener_driver.md) sends Events to any [Webhook](https://en.wikipedia.org/wiki/Webhook) URL.

```python
```

