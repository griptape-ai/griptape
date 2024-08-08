import requests

from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import PromptSummaryEngine
from griptape.loaders import PdfLoader

response = requests.get("https://arxiv.org/pdf/1706.03762.pdf")
engine = PromptSummaryEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
)

artifacts = PdfLoader().load(response.content)

if isinstance(artifacts, ErrorArtifact):
    raise Exception(artifacts.value)

text = "\n\n".join([a.value for a in artifacts])

engine.summarize_text(text)
