import wikipedia
from llama_index import GPTSimpleVectorIndex
from galaxybrain.tools import Tool
from llama_index import download_loader
from attrs import define


@define(frozen=True)
class Wiki(Tool):
    def run(self, args: dict[str]) -> str:
        article_search_queries = args.get("articles")
        question_query = args.get("query")
        nested_articles = [wikipedia.search(query, results=1) for query in article_search_queries]
        all_articles = []

        [all_articles.extend(articles) for articles in nested_articles if len(articles) > 0]

        if len(all_articles) > 0:
            loader = download_loader("WikipediaReader")()
            documents = loader.load_data(pages=all_articles, auto_suggest=False)
            index = GPTSimpleVectorIndex(documents)
            query_result = str(index.query(question_query)).strip()

            if query_result is None or query_result == "":
                return "query result is empty, try another search"
            else:
                return query_result
        else:
            return "no articles found"