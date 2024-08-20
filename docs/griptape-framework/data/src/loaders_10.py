from pathlib import Path

from griptape.loaders import AudioLoader
from griptape.utils import load_file

# Load an image from disk
audio_artifact = AudioLoader().load(Path("tests/resources/sentences.wav").read_bytes())

# You can also use the load_file utility function
AudioLoader().load(load_file("tests/resources/sentences.wav"))
