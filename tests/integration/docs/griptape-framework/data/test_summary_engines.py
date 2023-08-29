import re

class TestSummaryEngines:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/data/summary-engines/
    """
    def test_summary_engines(self):
        import io
        import requests
        from griptape.engines import PromptSummaryEngine
        from griptape.loaders import PdfLoader

        response = requests.get("https://arxiv.org/pdf/1706.03762.pdf")
        engine = PromptSummaryEngine()

        artifacts = PdfLoader().load(io.BytesIO(response.content))

        text = "\n\n".join([a.value for a in artifacts])

        result = engine.summarize_text(text)
        assert re.search('attention', result, re.IGNORECASE)
