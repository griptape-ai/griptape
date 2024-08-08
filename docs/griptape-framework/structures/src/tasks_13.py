from griptape.drivers import AmazonBedrockImageGenerationDriver, BedrockStableDiffusionImageGenerationModelDriver
from griptape.engines import InpaintingImageGenerationEngine
from griptape.loaders import ImageLoader
from griptape.structures import Pipeline
from griptape.tasks import InpaintingImageGenerationTask

# Create a driver configured to use Stable Diffusion via Bedrock.
driver = AmazonBedrockImageGenerationDriver(
    image_generation_model_driver=BedrockStableDiffusionImageGenerationModelDriver(),
    model="stability.stable-diffusion-xl-v0",
)

# Create an engine configured to use the driver.
engine = InpaintingImageGenerationEngine(
    image_generation_driver=driver,
)

# Load input image artifacts.
with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())

with open("tests/resources/mountain-mask.png", "rb") as f:
    mask_artifact = ImageLoader().load(f.read())

# Instantiate a pipeline.
pipeline = Pipeline()

# Add an InpaintingImageGenerationTask to the pipeline.
pipeline.add_task(
    InpaintingImageGenerationTask(
        input=("{{ args[0] }}", image_artifact, mask_artifact), image_generation_engine=engine, output_dir="images/"
    )
)

pipeline.run("An image of a castle built into the side of a mountain")
