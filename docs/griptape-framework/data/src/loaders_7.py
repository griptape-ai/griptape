from griptape.loaders import ImageLoader
from griptape.utils import load_file

# Load an image from disk
with open("tests/resources/mountain.png", "rb") as f:
    disk_image_artifact = ImageLoader().load(f.read())
# You can also use the load_file utility function
ImageLoader().load(load_file("tests/resources/mountain.png"))
