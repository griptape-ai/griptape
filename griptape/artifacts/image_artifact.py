from __future__ import annotations
from typing import Optional
from attr import define, field
from griptape.artifacts import BlobArtifact


@define(frozen=True)
class ImageArtifact(BlobArtifact):
    mime_type: str = field(kw_only=True)
    width: Optional[int] = field(default=None, kw_only=True)
    height: Optional[int] = field(default=None, kw_only=True)
    model: Optional[str] = field(default=None, kw_only=True)
    prompt: Optional[str] = field(default=None, kw_only=True)

    def to_text(self) -> str:
        return f"Image, dimensions: {self.width}x{self.height}, type: {self.mime_type}, size: {len(self.value)} bytes"

    def to_dict(self) -> dict:
        from griptape.schemas import ImageArtifactSchema

        return dict(ImageArtifactSchema().dump(self))
