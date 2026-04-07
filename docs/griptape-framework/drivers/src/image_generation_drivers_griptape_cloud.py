import os
from io import BytesIO

from PIL import Image

from griptape.drivers.image_generation.griptape_cloud import GriptapeCloudImageGenerationDriver

driver = GriptapeCloudImageGenerationDriver(
    api_key=os.environ["GT_CLOUD_API_KEY"],
    model="dall-e-3",
)


image = driver.run_text_to_image(["A capybara sitting on a rock in the sun."])

Image.open(BytesIO(image.value)).show()
