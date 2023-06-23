import threading
from queue import SimpleQueue
from typing import Callable
import logging
from attr import define, field, Factory
from time import sleep
from griptape.events.base_event import BaseEvent


@define
class EventQueueObserver:
    event_queue: SimpleQueue = field(kw_only=True)

    observables: dict[BaseEvent.BaseEventType, list[Callable[BaseEvent, None]]] = field(
        default={}, kw_only=True
    )

    poll_interval: float = field(default=0.1, kw_only=True)

    def __attrs_post_init__(self):
        event_thread = threading.Thread(target=self.watch_events, args=(), daemon=True)
        event_thread.start()

    def watch_events(self):
        while True:
            event = self.event_queue.get()
            event_handlers = self.observables.get(event.event_type, [])

            for event_handler in event_handlers:
                event_handler(event)
                sleep(self.poll_interval)
