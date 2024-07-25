import io
from abc import ABC
from typing import Optional, TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseDiffusionPipelineImageGenerationModelDriver, BaseImageGenerationDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from PIL import Image


@define
class HuggingFaceDiffusionPipelineImageGenerationDriver(BaseImageGenerationDriver, ABC):
    model_driver: BaseDiffusionPipelineImageGenerationModelDriver = field(kw_only=True, metadata={"serializable": True})
    device: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})

    def try_text_to_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        pipeline = self.model_driver.prepare_pipeline(self.model, self.device)

        prompt = ", ".join(prompts)
        output_image = pipeline(
            prompt, **self.model_driver.make_additional_params(negative_prompts, self.device)
        ).images[0]

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")

        return ImageArtifact(
            value=buffer.getvalue(), format="png", height=output_image.height, width=output_image.width, prompt=prompt
        )

    def try_image_variation(
        self, prompts: list[str], image: ImageArtifact, negative_prompts: Optional[list[str]] = None
    ) -> ImageArtifact:
        pipeline = self.model_driver.prepare_pipeline(self.model, self.device)

        prompt = ", ".join(prompts)
        Image = import_optional_dependency("PIL.Image")
        input_image = Image.open(io.BytesIO(image.value))

        # The size of the input image drives the size of the output image.
        # Resize the input image to the configured dimensions.
        requested_dimensions = self.model_driver.get_output_image_dimensions()
        if requested_dimensions is not None and (
            input_image.height != requested_dimensions[0] or input_image.width != requested_dimensions[1]
        ):
            input_image = input_image.resize(requested_dimensions)

        output_image = pipeline(
            prompt,
            **self.model_driver.make_image_param(input_image),
            **self.model_driver.make_additional_params(negative_prompts, self.device),
        ).images[0]

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")

        return ImageArtifact(
            value=buffer.getvalue(), format="png", height=output_image.height, width=output_image.width, prompt=prompt
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
