from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.drivers import BaseImageGenerationDriver
from griptape.exceptions import DummyError

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact


@define
class DummyImageGenerationDriver(BaseImageGenerationDriver):
    model: None = field(init=False, default=None, kw_only=True)

    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        raise DummyError(__class__.__name__, "try_text_to_image")

    def try_image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise DummyError(__class__.__name__, "try_image_variation")

    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise DummyError(__class__.__name__, "try_image_inpainting")

    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise DummyError(__class__.__name__, "try_image_outpainting")
