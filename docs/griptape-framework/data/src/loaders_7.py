from pathlib import Path

from griptape.loaders import ImageLoader
from griptape.utils import load_file

# Load an image from disk
disk_image_artifact = ImageLoader().load(Path("tests/resources/mountain.png").read_bytes())
# You can also use the load_file utility function
ImageLoader().load(load_file("tests/resources/mountain.png"))
