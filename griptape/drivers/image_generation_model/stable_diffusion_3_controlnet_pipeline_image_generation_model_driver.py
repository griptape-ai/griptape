import os
from typing import Any, Optional

from attrs import define, field
from diffusers.models.controlnet_sd3 import SD3ControlNetModel
from diffusers.pipelines.controlnet_sd3.pipeline_stable_diffusion_3_controlnet import StableDiffusion3ControlNetPipeline
from PIL.Image import Image

from griptape.drivers import StableDiffusion3PipelineImageGenerationModelDriver


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
        if os.path.isfile(self.controlnet_model):
            pipeline_params["controlnet"] = SD3ControlNetModel.from_single_file(
                self.controlnet_model, **controlnet_pipeline_params
            )

        else:
            pipeline_params["controlnet"] = SD3ControlNetModel.from_pretrained(
                self.controlnet_model, **controlnet_pipeline_params
            )

        if os.path.isfile(model):
            pipeline = StableDiffusion3ControlNetPipeline.from_single_file(model, **pipeline_params)

        else:
            pipeline = StableDiffusion3ControlNetPipeline.from_pretrained(model, **pipeline_params)

        if not isinstance(pipeline, StableDiffusion3ControlNetPipeline):
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
