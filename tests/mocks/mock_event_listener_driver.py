from attr import define

from griptape.drivers import BaseEventListenerDriver


@define
class MockEventListenerDriver(BaseEventListenerDriver):
    def try_publish_event(self, event_payload: dict) -> None:
        ...
