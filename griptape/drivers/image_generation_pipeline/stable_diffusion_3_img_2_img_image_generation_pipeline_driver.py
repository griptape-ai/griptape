from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import StableDiffusion3ImageGenerationPipelineDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from PIL.Image import Image


@define
class StableDiffusion3Img2ImgImageGenerationPipelineDriver(StableDiffusion3ImageGenerationPipelineDriver):
    """Image generation model driver for Stable Diffusion 3 model image to image pipelines.

    For more information, see the HuggingFace documentation for the StableDiffusion3Img2ImgPipeline:
        https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_diffusion_3/pipeline_stable_diffusion_3_img2img.py

    Attributes:
        strength: A value [0.0, 1.0] that determines the strength of the initial image in the output.
    """

    strength: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})

    def prepare_pipeline(self, model: str, device: Optional[str]) -> Any:
        sd3_img2img_pipeline = import_optional_dependency(
            "diffusers.pipelines.stable_diffusion_3.pipeline_stable_diffusion_3_img2img"
        ).StableDiffusion3Img2ImgPipeline

        pipeline_params = {}
        if self.torch_dtype is not None:
            pipeline_params["torch_dtype"] = self.torch_dtype

        if self.drop_t5_encoder:
            pipeline_params["text_encoder_3"] = None
            pipeline_params["tokenizer_3"] = None

        # A model can be provided either as a path to a local file
        # or as a HuggingFace model repo name.
        if os.path.isfile(model):
            # If the model provided is a local file (not a directory),
            # we load it using the from_single_file method.
            pipeline = sd3_img2img_pipeline.from_single_file(model, **pipeline_params)
        else:
            # If the model is a local directory or hosted on HuggingFace,
            # we load it using the from_pretrained method.
            pipeline = sd3_img2img_pipeline.from_pretrained(model, **pipeline_params)

        if self.enable_model_cpu_offload:
            pipeline.enable_model_cpu_offload()

        # Move inference to particular device if requested.
        if device is not None:
            pipeline.to(device)

        return pipeline

    def make_image_param(self, image: Optional[Image]) -> Optional[dict[str, Image]]:
        if image is None:
            raise ValueError("Input image is required for image to image pipelines.")

        return {"image": image}

    def make_additional_params(self, negative_prompts: Optional[list[str]], device: Optional[str]) -> dict[str, Any]:
        additional_params = super().make_additional_params(negative_prompts, device)

        # Explicit height and width params are not supported, but
        # are instead inferred from input image.
        del additional_params["height"]
        del additional_params["width"]

        if self.strength is not None:
            additional_params["strength"] = self.strength

        return additional_params
