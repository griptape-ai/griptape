from pathlib import Path

from griptape.loaders import ImageLoader

# Load an image from disk
ImageLoader().load("tests/resources/mountain.png")

# You can also pass a Path object
ImageLoader().load(Path("tests/resources/mountain.png"))
