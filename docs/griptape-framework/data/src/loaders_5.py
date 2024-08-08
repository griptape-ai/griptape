import urllib.request
from pathlib import Path

from griptape.loaders import TextLoader

TextLoader().load("my text")

urllib.request.urlretrieve("https://example-files.online-convert.com/document/txt/example.txt", "example.txt")

TextLoader().load(Path("example.txt").read_text())

TextLoader().load_collection(["my text", "my other text", Path("example.txt").read_text()])
