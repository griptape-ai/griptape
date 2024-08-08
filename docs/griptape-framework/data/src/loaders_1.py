import urllib.request

from griptape.loaders import PdfLoader
from griptape.utils import load_file, load_files

urllib.request.urlretrieve("https://arxiv.org/pdf/1706.03762.pdf", "attention.pdf")

# Load a single PDF file
with open("attention.pdf", "rb") as f:
    PdfLoader().load(f.read())
# You can also use the load_file utility function
PdfLoader().load(load_file("attention.pdf"))

urllib.request.urlretrieve("https://arxiv.org/pdf/1706.03762.pdf", "CoT.pdf")

# Load multiple PDF files
with open("attention.pdf", "rb") as attention, open("CoT.pdf", "rb") as cot:
    PdfLoader().load_collection([attention.read(), cot.read()])
# You can also use the load_files utility function
PdfLoader().load_collection(list(load_files(["attention.pdf", "CoT.pdf"]).values()))
