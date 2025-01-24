from griptape.drivers.image_generation.amazon_bedrock import AmazonBedrockImageGenerationDriver
from griptape.drivers.image_generation_model.bedrock_stable_diffusion import (
    BedrockStableDiffusionImageGenerationModelDriver,
)
from griptape.loaders import ImageLoader
from griptape.structures import Pipeline
from griptape.tasks import VariationImageGenerationTask

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v0",
)


# Load input image artifact.
image_artifact = ImageLoader().load("tests/resources/mountain.png")

# Instantiate a pipeline.
pipeline = Pipeline()

# Add a VariationImageGenerationTask to the pipeline.
pipeline.add_task(
    VariationImageGenerationTask(
        input=("{{ args[0] }}", image_artifact),
        image_generation_driver=driver,
        output_dir="images/",
    )
)

pipeline.run("An image of a mountain landscape on a snowy winter day")
