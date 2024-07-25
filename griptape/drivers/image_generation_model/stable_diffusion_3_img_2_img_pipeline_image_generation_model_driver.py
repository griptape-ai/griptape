from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import StableDiffusion3PipelineImageGenerationModelDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from diffusers.pipelines.stable_diffusion_3.pipeline_stable_diffusion_3_img2img import (
        StableDiffusion3Img2ImgPipeline,
    )
    from PIL.Image import Image


@define
class StableDiffusion3Img2ImgPipelineImageGenerationModelDriver(StableDiffusion3PipelineImageGenerationModelDriver):
    strength: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})

    def prepare_pipeline(self, model: str, device: Optional[str]) -> Any:
        pipeline_params = {}
        if self.torch_dtype is not None:
            pipeline_params["torch_dtype"] = self.torch_dtype

        # A model can be provided either as a path to a local file
        # or as a HuggingFace model repo name.
        sd3_img2img_pipeline = import_optional_dependency(
            "diffusers.pipelines.stable_diffusion_3.pipeline_stable_diffusion_3_img2img.StableDiffusion3Img2ImgPipeline"
        )
        if os.path.isfile(model):
            # If the model provided is a local file (not a directory),
            # we load it using the from_single_file method.

            raise NotImplementedError(
                "StableDiffusion3Img2ImgPipeline does not " "yet support loading from a single file."
            )
        else:
            # If the model is a local directory or hosted on HuggingFace,
            # we load it using the from_pretrained method.
            pipeline = sd3_img2img_pipeline.from_pretrained(model, **pipeline_params)

        if not isinstance(pipeline, StableDiffusion3Img2ImgPipeline):
            raise ValueError(f"Expected StableDiffusion3Img2ImgPipeline, but got {type(pipeline)}.")

        # Move inference to particular device if requested.
        if device is not None:
            pipeline.to(device)

        return pipeline

    def make_image_param(self, image: Optional[Image]) -> Optional[dict[str, Image]]:
        if image is None:
            return None

        return {"input_image": image}

    def make_additional_params(self, negative_prompts: Optional[list[str]], device: Optional[str]) -> dict[str, Any]:
        additional_params = super().make_additional_params(negative_prompts, device)

        # Explicit height and width params are not supported, but
        # are instead inferred from input image.
        del additional_params["height"]
        del additional_params["width"]

        if self.strength is not None:
            additional_params["strength"] = self.strength

        return additional_params
