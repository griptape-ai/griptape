from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers.image_generation_model.base_diffusion_pipeline_image_generation_model_driver import (
    BaseDiffusionPipelineImageGenerationModelDriver,
)
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import torch
    from diffusers.pipelines.stable_diffusion_3.pipeline_stable_diffusion_3 import StableDiffusion3Pipeline
    from PIL.Image import Image


@define
class StableDiffusion3PipelineImageGenerationModelDriver(BaseDiffusionPipelineImageGenerationModelDriver):
    width: int = field(default=1024, kw_only=True, metadata={"serializable": True})
    height: int = field(default=1024, kw_only=True, metadata={"serializable": True})
    seed: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    guidance_scale: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    steps: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    torch_dtype: Optional[torch.dtype] = field(default=None, kw_only=True, metadata={"serializable": True})

    def prepare_pipeline(self, model: str, device: Optional[str]) -> Any:
        pipeline_params = {}
        if self.torch_dtype is not None:
            pipeline_params["torch_dtype"] = self.torch_dtype

        # A model can be provided either as a path to a local file
        # or as a HuggingFace model repo name.
        sd3_pipeline = import_optional_dependency(
            "diffusers.pipelines.stable_diffusion_3.pipeline_stable_diffusion_3.StableDiffusion3Pipeline"
        )
        if os.path.isfile(model):
            # If the model provided is a local file (not a directory),
            # we load it using the from_single_file method.
            pipeline = sd3_pipeline.from_single_file(model, **pipeline_params)
        else:
            # If the model is a local directory or hosted on HuggingFace,
            # we load it using the from_pretrained method.
            pipeline = sd3_pipeline.from_pretrained(model, **pipeline_params)

        if not isinstance(pipeline, StableDiffusion3Pipeline):
            raise ValueError(f"Expected StableDiffusion3Pipeline, but got {type(pipeline)}.")

        # Move inference to particular device if requested.
        if device is not None:
            pipeline.to(device)

        return pipeline

    def make_image_param(self, image: Optional[Image]) -> Optional[dict[str, Image]]:
        return None

    def make_additional_params(self, negative_prompts: Optional[list[str]], device: Optional[str]) -> dict[str, Any]:
        additional_params = {}
        if negative_prompts:
            additional_params["negative_prompt"] = ", ".join(negative_prompts)

        if self.width is not None:
            additional_params["width"] = self.width

        if self.height is not None:
            additional_params["height"] = self.height

        if self.seed is not None:
            additional_params["generator"] = [torch.Generator(device=device).manual_seed(self.seed)]

        if self.guidance_scale is not None:
            additional_params["guidance_scale"] = self.guidance_scale

        if self.steps is not None:
            additional_params["num_inference_steps"] = self.steps

        return additional_params

    def get_output_image_dimensions(self) -> tuple[int, int]:
        return self.width, self.height
