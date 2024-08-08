from griptape.loaders import ImageLoader
from griptape.utils import load_file, load_files

# Load a single image in BMP format
with open("tests/resources/mountain.png", "rb") as f:
    image_artifact_jpeg = ImageLoader(format="bmp").load(f.read())
# You can also use the load_file utility function
ImageLoader(format="bmp").load(load_file("tests/resources/mountain.png"))

# Load multiple images in BMP format
with open("tests/resources/mountain.png", "rb") as mountain, open("tests/resources/cow.png", "rb") as cow:
    ImageLoader().load_collection([mountain.read(), cow.read()])
# You can also use the load_files utility function
ImageLoader().load_collection(list(load_files(["tests/resources/mountain.png", "tests/resources/cow.png"]).values()))
