from pathlib import Path

from griptape.loaders import JsonLoader

# Load an image from disk
JsonLoader().load("tests/resources/test.json")

# You can also pass a Path object
JsonLoader().load(Path("tests/resources/test.json"))
