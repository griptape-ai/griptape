from attrs import define, field

from griptape.events.base_chunk_event import BaseChunkEvent


@define
class TextChunkEvent(BaseChunkEvent):
    token: str = field(kw_only=True, metadata={"serializable": True})

    def __str__(self) -> str:
        return self.token
