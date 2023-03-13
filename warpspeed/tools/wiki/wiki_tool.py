import logging
import wikipedia
from llama_index import GPTSimpleVectorIndex, Document
from warpspeed.structures import Structure
from warpspeed.tools import Tool
from attrs import define


@define
class WikiTool(Tool):
    def run(self, args: dict[str]) -> str:
        article_search_queries = args.get("articles")
        question_query = args.get("query")
        nested_articles = [wikipedia.search(query, results=1) for query in article_search_queries]
        all_articles = []

        [all_articles.extend(articles) for articles in nested_articles if len(articles) > 0]

        if len(all_articles) > 0:
            documents = []

            for article in all_articles:
                try:
                    content = wikipedia.page(article, auto_suggest=False).content

                    documents.append(Document(content))
                except Exception as e:
                    logging.getLogger(Structure.LOGGER_NAME).error(f"Error loading Wikipedia article '{article}': {e}")

            index = GPTSimpleVectorIndex(documents)
            query_result = str(index.query(question_query)).strip()

            if query_result is None or query_result == "":
                return "query result is empty, try another search"
            else:
                return query_result
        else:
            return "no articles found"
