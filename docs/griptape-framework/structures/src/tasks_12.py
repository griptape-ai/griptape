from pathlib import Path

from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.engines import VariationImageGenerationEngine
from griptape.loaders import ImageLoader
from griptape.structures import Pipeline
from griptape.tasks import VariationImageGenerationTask

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v0",
)

# Create an engine configured to use the driver.
engine = VariationImageGenerationEngine(
    image_generation_driver=driver,
)

# Load input image artifact.
image_artifact = ImageLoader().load(Path("tests/resources/mountain.png").read_bytes())

# Instantiate a pipeline.
pipeline = Pipeline()

# Add a VariationImageGenerationTask to the pipeline.
pipeline.add_task(
    VariationImageGenerationTask(
        input=("{{ args[0] }}", image_artifact),
        image_generation_engine=engine,
        output_dir="images/",
    )
)

pipeline.run("An image of a mountain landscape on a snowy winter day")
