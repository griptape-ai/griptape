import requests

from griptape.drivers import OpenAiChatPromptDriver
from griptape.engines import PromptSummaryEngine
from griptape.loaders import PdfLoader

response = requests.get("https://arxiv.org/pdf/1706.03762.pdf")
engine = PromptSummaryEngine(
    prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo"),
)

artifact = PdfLoader().parse(response.content)

engine.summarize_artifacts(artifact)
