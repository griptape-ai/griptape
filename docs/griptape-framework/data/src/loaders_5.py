import urllib.request
from pathlib import Path

from griptape.loaders import TextLoader

TextLoader().load("tests/resources/test.txt")

urllib.request.urlretrieve("https://example-files.online-convert.com/document/txt/example.txt", "example.txt")

TextLoader().load(Path("example.txt"))

TextLoader().load_collection(["tests/resources/test.txt", Path("example.txt")])
