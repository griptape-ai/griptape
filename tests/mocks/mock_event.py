from griptape.events import BaseEvent


class MockEvent(BaseEvent):
    def to_dict(self) -> dict:
        return {"timestamp": self.timestamp, "id": self.id, "meta": self.meta, "type": self.__class__.__name__}
