# Structure Run Events

Running a Structure will result in Events being created for that Structure Run. Events are used to report data about the progress of your Structure Run. There are two types of Events: `SYSTEM` Events and `USER` Events.

For information about the Events APIs, check out the [Events API docs](../api/api-reference.md/#/Events).

## Event Types

### System Events

The Griptape Cloud Structure Runtime manages the lifecycle of your Structure Run. To communicate near real-time updates about the status of your Structure Run, the Cloud will emit `SYSTEM` Events.

The following types of `SYSTEM` Events are emitted:

1. `StructureRunStarting`
1. `StructureRunRunning`
1. `StructureRunCompleted`
1. `StructureRunError`

#### StructureRunStarting

This Event indicates that your Structure code has been successfully loaded in the Runtime.

Example Event body:

```json
{
    "event_id": "12345678-1909-4900-8eca-6f7d82da9fdc",
    "timestamp": 1726096542.71688,
    "type": "StructureRunStarting",
    "payload": {
        "status": "STARTING"
    },
    "created_at": "2024-09-11T23:15:42.834783Z",
    "origin": "SYSTEM",
    "structure_run": "12345678-e125-4c38-b67f-02b82aa443ce"
}
```

#### StructureRunRunning

This Event indicates that your Structure code is now executing.

Example Event body:

```json
{
    "event_id": "22345678-1909-4900-8eca-6f7d82da9fdc",
    "timestamp": 1726096548.683578,
    "type": "StructureRunRunning",
    "payload": {
        "status": "RUNNING",
        "started_at": "2024-09-11T23:15:47"
    },
    "created_at": "2024-09-11T23:15:48.787162Z",
    "origin": "SYSTEM",
    "structure_run": "12345678-e125-4c38-b67f-02b82aa443ce"
}
```

#### StructureRunCompleted

This Event indicates that your Structure code has exited.

Example Event body:

```json
{
    "event_id": "32345678-f277-4f12-939f-707804f2fdf0",
    "timestamp": 1726096554.70717,
    "type": "StructureRunCompleted",
    "payload": {
        "status": "SUCCEEDED",
        "started_at": "2024-09-11T23:15:47",
        "completed_at": "2024-09-11T23:15:50",
        "status_detail": {
            "reason": "Completed",
            "message": null,
            "exit_code": 0
        }
    },
    "created_at": "2024-09-11T23:15:54.754921Z",
    "origin": "SYSTEM",
    "structure_run": "12345678-e125-4c38-b67f-02b82aa443ce"
}
```

#### StructureRunError

This Event indicates that your Structure Run encountered an Error from the Griptape Cloud Runtime.

Example Event body:

```json
{
    "event_id": "42345678-f277-4f12-939f-707804f2fdf0",
    "timestamp": 1726096555.70717,
    "type": "StructureRunError",
    "payload": {
        "status": "ERROR",
        "status_detail": {
            "error": "Error message"
        }
    },
    "created_at": "2024-09-11T23:15:54.754921Z",
    "origin": "SYSTEM",
    "structure_run": "12345678-e125-4c38-b67f-02b82aa443ce"
}
```

### User Events

User Events are any Events emitted by your Structure code to the Events API. The recommended approach for emitting those Events is to make use of the
[Griptape Cloud Event Listener Driver](../../griptape-framework/drivers/event-listener-drivers.md#griptape-cloud) in the Griptape framework.

For a full example of Structure code that makes use of that driver, refer to the [Managed Structure Template](https://github.com/griptape-ai/managed-structure-template/blob/main/structure.py).

#### Structure Run Output

In order for Griptape Cloud to populate the `output` field for your Structure Run, there needs to be a `USER` Event of type `FinishStructureRunEvent`.

By using the Griptape Cloud Event Listener Driver and an [Event Bus](../../griptape-framework/misc/events.md) that emits that Event type in your Structure code, the Cloud will automatically populate your Structure Run's output.

## Example Client Event Listener

For an example of client code listening to Structure Run Events, check out the example client in the
[Managed Structure Template](https://github.com/griptape-ai/managed-structure-template/blob/main/example-client/client.py).
