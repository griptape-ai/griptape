from pathlib import Path

from griptape.loaders import ImageLoader

# Load a single image in BMP format
ImageLoader(format="bmp").load("tests/resources/mountain.png")
# You can also pass a Path object
ImageLoader(format="bmp").load(Path("tests/resources/mountain.png"))

# Load multiple images in BMP format
ImageLoader().load_collection([Path("tests/resources/mountain.png"), "tests/resources/cow.png"])
