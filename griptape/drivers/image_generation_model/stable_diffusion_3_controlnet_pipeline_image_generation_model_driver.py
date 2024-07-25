from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.drivers import StableDiffusion3PipelineImageGenerationModelDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from PIL.Image import Image


@define
class StableDiffusion3ControlNetPipelineImageGenerationModelDriver(StableDiffusion3PipelineImageGenerationModelDriver):
    controlnet_model: str = field(kw_only=True)
    controlnet_conditioning_scale: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})

    def prepare_pipeline(self, model: str, device: Optional[str]) -> Any:
        pipeline_params = {}
        controlnet_pipeline_params = {}
        if self.torch_dtype is not None:
            pipeline_params["torch_dtype"] = self.torch_dtype
            controlnet_pipeline_params["torch_dtype"] = self.torch_dtype

        # For both Stable Diffusion and ControlNet, models can be provided either
        # as a path to a local file or as a HuggingFace model repo name.
        # We use the from_single_file method if the model is a local file and the
        # from_pretrained method if the model is a local directory or hosted on HuggingFace.
        sd3_controlnet_model = import_optional_dependency("diffusers.models.controlnet_sd3").SD3ControlNetModel
        if os.path.isfile(self.controlnet_model):
            pipeline_params["controlnet"] = sd3_controlnet_model.from_single_file(
                self.controlnet_model, **controlnet_pipeline_params
            )

        else:
            pipeline_params["controlnet"] = sd3_controlnet_model.from_pretrained(
                self.controlnet_model, **controlnet_pipeline_params
            )

        sd3_controlnet_pipeline = import_optional_dependency(
            "diffusers.pipelines.controlnet_sd3.pipeline_stable_diffusion_3_controlnet"
        ).StableDiffusion3ControlNetPipeline
        if os.path.isfile(model):
            pipeline = sd3_controlnet_pipeline.from_single_file(model, **pipeline_params)

        else:
            pipeline = sd3_controlnet_pipeline.from_pretrained(model, **pipeline_params)

        if not isinstance(pipeline, sd3_controlnet_pipeline):
            raise ValueError(f"Expected StableDiffusion3ControlNetPipeline, but got {type(pipeline)}.")

        if device is not None:
            pipeline.to(device)

        return pipeline

    def make_image_param(self, image: Optional[Image]) -> Optional[dict[str, Image]]:
        if image is None:
            return None

        return {"control_image": image}

    def make_additional_params(self, negative_prompts: Optional[list[str]], device: Optional[str]) -> dict[str, Any]:
        additional_params = super().make_additional_params(negative_prompts, device)

        del additional_params["height"]
        del additional_params["width"]

        if self.controlnet_conditioning_scale is not None:
            additional_params["controlnet_conditioning_scale"] = self.controlnet_conditioning_scale

        return additional_params
