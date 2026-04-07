from griptape.artifacts import TextArtifact
from griptape.drivers.image_generation.huggingface_pipeline import HuggingFacePipelineImageGenerationDriver
from griptape.drivers.image_generation_pipeline.stable_diffusion_3_controlnet import (
    StableDiffusion3ControlNetImageGenerationPipelineDriver,
)
from griptape.loaders import ImageLoader
from griptape.structures import Pipeline
from griptape.tasks import VariationImageGenerationTask

prompt_artifact = TextArtifact("landscape photograph, verdant, countryside, 8k")
control_image_artifact = ImageLoader().load("canny_control_image.png")

controlnet_task = VariationImageGenerationTask(
    input=(prompt_artifact, control_image_artifact),
    image_generation_driver=HuggingFacePipelineImageGenerationDriver(
        model="stabilityai/stable-diffusion-3-medium-diffusers",
        device="cuda",
        pipeline_driver=StableDiffusion3ControlNetImageGenerationPipelineDriver(
            controlnet_model="InstantX/SD3-Controlnet-Canny",
            height=768,
            width=1024,
        ),
    ),
)

output_artifact = Pipeline(tasks=[controlnet_task]).run().output
