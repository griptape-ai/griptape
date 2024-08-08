from griptape.loaders import AudioLoader
from griptape.utils import load_file

# Load an image from disk
with open("tests/resources/sentences.wav", "rb") as f:
    audio_artifact = AudioLoader().load(f.read())

# You can also use the load_file utility function
AudioLoader().load(load_file("tests/resources/sentences.wav"))
