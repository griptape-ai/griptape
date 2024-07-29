from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import StableDiffusion3ImageGenerationPipelineDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from PIL.Image import Image


@define
class StableDiffusion3ControlNetImageGenerationPipelineDriver(StableDiffusion3ImageGenerationPipelineDriver):
    """Image generation model driver for Stable Diffusion 3 models with ControlNet.

    For more information, see the HuggingFace documentation for the StableDiffusion3ControlNetPipeline:
        https://huggingface.co/docs/diffusers/en/api/pipelines/controlnet_sd3

    Attributes:
        controlnet_model: The ControlNet model to use for image generation.
        controlnet_conditioning_scale: The conditioning scale for the ControlNet model. Defaults to None.
    """

    controlnet_model: str = field(kw_only=True)
    controlnet_conditioning_scale: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})

    def prepare_pipeline(self, model: str, device: Optional[str]) -> Any:
        sd3_controlnet_model = import_optional_dependency("diffusers.models.controlnet_sd3").SD3ControlNetModel
        sd3_controlnet_pipeline = import_optional_dependency(
            "diffusers.pipelines.controlnet_sd3.pipeline_stable_diffusion_3_controlnet"
        ).StableDiffusion3ControlNetPipeline

        pipeline_params = {}
        controlnet_pipeline_params = {}
        if self.torch_dtype is not None:
            pipeline_params["torch_dtype"] = self.torch_dtype
            controlnet_pipeline_params["torch_dtype"] = self.torch_dtype

        if self.drop_t5_encoder:
            pipeline_params["text_encoder_3"] = None
            pipeline_params["tokenizer_3"] = None

        # For both Stable Diffusion and ControlNet, models can be provided either
        # as a path to a local file or as a HuggingFace model repo name.
        # We use the from_single_file method if the model is a local file and the
        # from_pretrained method if the model is a local directory or hosted on HuggingFace.
        if os.path.isfile(self.controlnet_model):
            pipeline_params["controlnet"] = sd3_controlnet_model.from_single_file(
                self.controlnet_model, **controlnet_pipeline_params
            )
        else:
            pipeline_params["controlnet"] = sd3_controlnet_model.from_pretrained(
                self.controlnet_model, **controlnet_pipeline_params
            )

        if os.path.isfile(model):
            pipeline = sd3_controlnet_pipeline.from_single_file(model, **pipeline_params)
        else:
            pipeline = sd3_controlnet_pipeline.from_pretrained(model, **pipeline_params)

        if self.enable_model_cpu_offload:
            pipeline.enable_model_cpu_offload()

        if device is not None:
            pipeline.to(device)

        return pipeline

    def make_image_param(self, image: Optional[Image]) -> Optional[dict[str, Image]]:
        if image is None:
            raise ValueError("Input image is required for ControlNet pipelines.")

        return {"control_image": image}

    def make_additional_params(self, negative_prompts: Optional[list[str]], device: Optional[str]) -> dict[str, Any]:
        additional_params = super().make_additional_params(negative_prompts, device)

        del additional_params["height"]
        del additional_params["width"]

        if self.controlnet_conditioning_scale is not None:
            additional_params["controlnet_conditioning_scale"] = self.controlnet_conditioning_scale

        return additional_params
