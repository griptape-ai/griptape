from pathlib import Path

from griptape.artifacts import TextArtifact
from griptape.drivers import (
    HuggingFacePipelineImageGenerationDriver,
    StableDiffusion3Img2ImgImageGenerationPipelineDriver,
)
from griptape.engines import VariationImageGenerationEngine
from griptape.loaders import ImageLoader
from griptape.structures import Pipeline
from griptape.tasks import VariationImageGenerationTask

prompt_artifact = TextArtifact("landscape photograph, verdant, countryside, 8k")
input_image_artifact = ImageLoader().load(Path("tests/resources/mountain.png").read_bytes())

image_variation_task = VariationImageGenerationTask(
    input=(prompt_artifact, input_image_artifact),
    image_generation_engine=VariationImageGenerationEngine(
        image_generation_driver=HuggingFacePipelineImageGenerationDriver(
            model="stabilityai/stable-diffusion-3-medium-diffusers",
            device="cuda",
            pipeline_driver=StableDiffusion3Img2ImgImageGenerationPipelineDriver(
                height=1024,
                width=1024,
            ),
        )
    ),
)

output_artifact = Pipeline(tasks=[image_variation_task]).run().output
