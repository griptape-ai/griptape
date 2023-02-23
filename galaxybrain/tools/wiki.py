import wikipedia
from galaxybrain.tools import Tool
from galaxybrain.utils import J2


class Wiki(Tool):
    sentences: int

    def __init__(self, sentences: int = 10):
        self.name = "wiki"
        self.description =\
            "This tool can search wikipedia. Keep your search terms short."
        self.examples =\
            J2("tools/wiki/examples.j2").render()
        self.sentences = sentences

    def run(self, value: str) -> str:
        results = wikipedia.search(value)

        if len(results) > 0:
            return wikipedia.summary(results[0], sentences=self.sentences, auto_suggest=False)
        else:
            return "no results found for this query"
