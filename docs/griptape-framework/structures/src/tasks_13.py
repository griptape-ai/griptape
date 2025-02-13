from griptape.drivers.image_generation.amazon_bedrock import AmazonBedrockImageGenerationDriver
from griptape.drivers.image_generation_model.bedrock_stable_diffusion import (
    BedrockStableDiffusionImageGenerationModelDriver,
)
from griptape.loaders import ImageLoader
from griptape.structures import Pipeline
from griptape.tasks import InpaintingImageGenerationTask

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v1",
)

# Load input image artifacts.
image_artifact = ImageLoader().load("tests/resources/mountain.png")

mask_artifact = ImageLoader().load("tests/resources/mountain-mask.png")

# Instantiate a pipeline.
pipeline = Pipeline()

# Add an InpaintingImageGenerationTask to the pipeline.
pipeline.add_task(
    InpaintingImageGenerationTask(
        input=("{{ args[0] }}", image_artifact, mask_artifact), image_generation_driver=driver, output_dir="images/"
    )
)

pipeline.run("An image of a castle built into the side of a mountain")
