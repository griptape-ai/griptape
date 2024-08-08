import urllib

from griptape.loaders import TextLoader

TextLoader().load("my text")

urllib.request.urlretrieve("https://example-files.online-convert.com/document/txt/example.txt", "example.txt")

with open("example.txt") as f:
    TextLoader().load(f.read())

with open("example.txt") as f:
    TextLoader().load_collection(["my text", "my other text", f.read()])
