from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attr import define, field

from griptape.artifacts import ImageArtifact
from griptape.events import StartImageGenerationEvent, FinishImageGenerationEvent
from griptape.mixins import ExponentialBackoffMixin

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class BaseImageGenerationDriver(ExponentialBackoffMixin, ABC):
    model: str = field(kw_only=True)
    structure: Optional[Structure] = field(default=None, kw_only=True)

    def before_run(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> None:
        if self.structure:
            self.structure.publish_event(StartImageGenerationEvent(prompts=prompts, negative_prompts=negative_prompts))

    def after_run(self) -> None:
        if self.structure:
            self.structure.publish_event(FinishImageGenerationEvent())

    def run_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompts, negative_prompts)
                result = self.try_text_to_image(prompts, negative_prompts)
                self.after_run()

                return result

        else:
            raise Exception("Failed to run text to image generation")

    def run_image_variation(
        self, prompts: list[str], image: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompts, negative_prompts)
                result = self.try_image_variation(prompts, image, negative_prompts)
                self.after_run()

                return result

        else:
            raise Exception("Failed to generate image variations")

    def run_image_inpainting(
        self, prompts: list[str], image: ImageArtifact, mask: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompts, negative_prompts)
                result = self.try_image_inpainting(prompts, image, mask, negative_prompts)
                self.after_run()

                return result

        else:
            raise Exception("Failed to run image inpainting")

    def run_image_outpainting(
        self, prompts: list[str], image: ImageArtifact, mask: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompts, negative_prompts)
                result = self.try_image_outpainting(prompts, image, mask, negative_prompts)
                self.after_run()

                return result

        else:
            raise Exception("Failed to run image outpainting")

    @abstractmethod
    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        ...

    @abstractmethod
    def try_image_variation(
        self, prompts: list[str], image: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        ...

    @abstractmethod
    def try_image_inpainting(
        self, prompts: list[str], image: ImageArtifact, mask: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        ...

    @abstractmethod
    def try_image_outpainting(
        self, prompts: list[str], image: ImageArtifact, mask: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        ...
