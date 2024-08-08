import urllib.request
from pathlib import Path

from griptape.loaders import PdfLoader
from griptape.utils import load_file, load_files

urllib.request.urlretrieve("https://arxiv.org/pdf/1706.03762.pdf", "attention.pdf")

# Load a single PDF file
PdfLoader().load(Path("attention.pdf").read_bytes())
# You can also use the load_file utility function
PdfLoader().load(load_file("attention.pdf"))

urllib.request.urlretrieve("https://arxiv.org/pdf/1706.03762.pdf", "CoT.pdf")

# Load multiple PDF files
PdfLoader().load_collection([Path("attention.pdf").read_bytes(), Path("CoT.pdf").read_bytes()])
# You can also use the load_files utility function
PdfLoader().load_collection(list(load_files(["attention.pdf", "CoT.pdf"]).values()))
