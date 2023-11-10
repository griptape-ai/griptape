from griptape.memory.meta import BaseMetaEntry


class MockMetaEntry(BaseMetaEntry):
    def to_dict(self) -> dict:
        return {"foo": "bar"}
