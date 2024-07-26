from __future__ import annotations

import io
from abc import ABC
from typing import Optional

from attrs import define, field

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseDiffusionImageGenerationPipelineDriver, BaseImageGenerationDriver
from griptape.utils import import_optional_dependency


@define
class HuggingFacePipelineImageGenerationDriver(BaseImageGenerationDriver, ABC):
    """Image generation driver for models hosted by Hugging Face's Diffusion Pipeline.

    For more information, see the HuggingFace documentation for Diffusers:
            https://huggingface.co/docs/diffusers/en/index

    Attributes:
        pipeline_driver: A pipeline image generation model driver typed for the specific pipeline required by the model.
        device: The hardware device used for inference. For example, "cpu", "cuda", or "mps".
        output_format: The format the generated image is returned in. Defaults to "png".
    """

    pipeline_driver: BaseDiffusionImageGenerationPipelineDriver = field(kw_only=True, metadata={"serializable": True})
    device: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    output_format: str = field(default="png", kw_only=True, metadata={"serializable": True})

    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        pipeline = self.pipeline_driver.prepare_pipeline(self.model, self.device)

        prompt = ", ".join(prompts)
        output_image = pipeline(
            prompt, **self.pipeline_driver.make_additional_params(negative_prompts, self.device)
        ).images[0]

        buffer = io.BytesIO()
        output_image.save(buffer, format=self.output_format.upper())

        return ImageArtifact(
            value=buffer.getvalue(),
            format=self.output_format.lower(),
            height=output_image.height,
            width=output_image.width,
            prompt=prompt,
        )

    def try_image_variation(
        self, prompts: list[str], image: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        pil_image = import_optional_dependency("PIL.Image")

        pipeline = self.pipeline_driver.prepare_pipeline(self.model, self.device)

        prompt = ", ".join(prompts)
        input_image = pil_image.open(io.BytesIO(image.value))
        # The size of the input image drives the size of the output image.
        # Resize the input image to the configured dimensions.
        output_width, output_height = self.pipeline_driver.output_image_dimensions
        if input_image.height != output_height or input_image.width != output_width:
            input_image = input_image.resize((output_width, output_height))

        output_image = pipeline(
            prompt,
            **self.pipeline_driver.make_image_param(input_image),
            **self.pipeline_driver.make_additional_params(negative_prompts, self.device),
        ).images[0]

        buffer = io.BytesIO()
        output_image.save(buffer, format=self.output_format.upper())

        return ImageArtifact(
            value=buffer.getvalue(),
            format=self.output_format.lower(),
            height=output_image.height,
            width=output_image.width,
            prompt=prompt,
        )

    def try_image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NotImplementedError("Inpainting is not supported by this driver.")

    def try_image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
    ) -> ImageArtifact:
        raise NotImplementedError("Outpainting is not supported by this driver.")
