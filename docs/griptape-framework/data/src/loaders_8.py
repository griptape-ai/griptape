from pathlib import Path

from griptape.loaders import ImageLoader
from griptape.utils import load_file, load_files

# Load a single image in BMP format
image_artifact_jpeg = ImageLoader(format="bmp").load(Path("tests/resources/mountain.png").read_bytes())
# You can also use the load_file utility function
ImageLoader(format="bmp").load(load_file("tests/resources/mountain.png"))

# Load multiple images in BMP format
ImageLoader().load_collection(
    [Path("tests/resources/mountain.png").read_bytes(), Path("tests/resources/cow.png").read_bytes()]
)
# You can also use the load_files utility function
ImageLoader().load_collection(list(load_files(["tests/resources/mountain.png", "tests/resources/cow.png"]).values()))
