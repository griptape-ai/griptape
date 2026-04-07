from pathlib import Path

from griptape.loaders import AudioLoader

# Load an image from disk
AudioLoader().load("tests/resources/sentences.wav")

# You can also pass a Path object
AudioLoader().load(Path("tests/resources/sentences.wav"))
