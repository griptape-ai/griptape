from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers.image_generation_pipeline.base_image_generation_pipeline_driver import (
    BaseDiffusionImageGenerationPipelineDriver,
)
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import torch
    from PIL.Image import Image


@define
class StableDiffusion3ImageGenerationPipelineDriver(BaseDiffusionImageGenerationPipelineDriver):
    """Image generation model driver for Stable Diffusion 3 models.

    For more information, see the HuggingFace documentation for the StableDiffusion3Pipeline:
        https://huggingface.co/docs/diffusers/main/en/api/pipelines/stable_diffusion/stable_diffusion_3

    Attributes:
        width: The width of the generated image. Defaults to 1024. Must be a multiple of 64.
        height: The height of the generated image. Defaults to 1024. Must be a multiple of 64.
        seed: The random seed to use for image generation. If not provided, a random seed will be used.
        guidance_scale: The strength of the guidance loss. If not provided, the default value will be used.
        steps: The number of inference steps to use in image generation. If not provided, the default value will be used.
        torch_dtype: The torch data type to use for image generation. If not provided, the default value will be used.
    """

    width: int = field(default=1024, kw_only=True, metadata={"serializable": True})
    height: int = field(default=1024, kw_only=True, metadata={"serializable": True})
    seed: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    guidance_scale: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    steps: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    torch_dtype: Optional[torch.dtype] = field(default=None, kw_only=True, metadata={"serializable": True})
    enable_model_cpu_offload: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    drop_t5_encoder: bool = field(default=False, kw_only=True, metadata={"serializable": True})

    def prepare_pipeline(self, model: str, device: Optional[str]) -> Any:
        sd3_pipeline = import_optional_dependency(
            "diffusers.pipelines.stable_diffusion_3.pipeline_stable_diffusion_3"
        ).StableDiffusion3Pipeline

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
            pipeline = sd3_pipeline.from_single_file(model, **pipeline_params)
        else:
            # If the model is a local directory or hosted on HuggingFace,
            # we load it using the from_pretrained method.
            pipeline = sd3_pipeline.from_pretrained(model, **pipeline_params)

        if self.enable_model_cpu_offload:
            pipeline.enable_model_cpu_offload()

        # Move inference to particular device if requested.
        if device is not None:
            pipeline.to(device)

        return pipeline

    def make_image_param(self, image: Optional[Image]) -> Optional[dict[str, Image]]:
        return None

    def make_additional_params(self, negative_prompts: Optional[list[str]], device: Optional[str]) -> dict[str, Any]:
        torch_generator = import_optional_dependency("torch").Generator

        additional_params = {}
        if negative_prompts:
            additional_params["negative_prompt"] = ", ".join(negative_prompts)

        if self.width is not None:
            additional_params["width"] = self.width

        if self.height is not None:
            additional_params["height"] = self.height

        if self.seed is not None:
            additional_params["generator"] = [torch_generator(device=device).manual_seed(self.seed)]

        if self.guidance_scale is not None:
            additional_params["guidance_scale"] = self.guidance_scale

        if self.steps is not None:
            additional_params["num_inference_steps"] = self.steps

        return additional_params

    @property
    def output_image_dimensions(self) -> tuple[int, int]:
        return self.width, self.height
