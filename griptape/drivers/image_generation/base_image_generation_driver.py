from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.events import FinishImageGenerationEvent, StartImageGenerationEvent
from griptape.mixins import EventPublisherMixin, ExponentialBackoffMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact


@define
class BaseImageGenerationDriver(EventPublisherMixin, SerializableMixin, ExponentialBackoffMixin, ABC):
    model: str = field(kw_only=True, metadata={"serializable": True})

    def before_run(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> None:
        self.publish_event(StartImageGenerationEvent(prompts=prompts, negative_prompts=negative_prompts))

    def after_run(self) -> None:
        self.publish_event(FinishImageGenerationEvent())

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
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
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
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
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
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
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
    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact: ...

    @abstractmethod
    def try_image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact: ...

    @abstractmethod
    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact: ...

    @abstractmethod
    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact: ...
