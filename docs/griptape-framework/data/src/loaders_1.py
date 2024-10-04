import urllib.request
from pathlib import Path

from griptape.loaders import PdfLoader

urllib.request.urlretrieve("https://arxiv.org/pdf/1706.03762.pdf", "attention.pdf")

# Load a single PDF file
PdfLoader().load("attention.pdf")
# You can also pass a Path object
PdfLoader().load(Path("attention.pdf"))

urllib.request.urlretrieve("https://arxiv.org/pdf/1706.03762.pdf", "CoT.pdf")

# Load multiple PDF files
PdfLoader().load_collection([Path("attention.pdf"), Path("CoT.pdf")])
