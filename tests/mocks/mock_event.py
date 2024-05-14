from griptape.events import BaseEvent


class MockEvent(BaseEvent):
    def to_dict(self) -> dict:
        return {"timestamp": self.timestamp, "id": self.id}
