import re

class TestLoadAndQueryPinecone:
    """
    https://docs.griptape.ai/en/latest/examples/load-query-and-chat-marqo/
    """

    def test_load_and_query_pinecone(self):
        import hashlib
        import os
        import json
        from urllib.request import urlopen
        from griptape.drivers import PineconeVectorStoreDriver

        def load_data(driver: PineconeVectorStoreDriver) -> None:
            response = urlopen(
                "https://raw.githubusercontent.com/wedeploy-examples/"
                "supermarket-web-example/master/products.json"
            )

            for product in json.loads(response.read()):
                driver.upsert_text(
                    product["description"],
                    vector_id=hashlib.md5(product["title"].encode()).hexdigest(),
                    meta={
                        "title": product["title"],
                        "description": product["description"],
                        "type": product["type"],
                        "price": product["price"],
                        "rating": product["rating"],
                    },
                    namespace="supermarket-products",
                )

        vector_driver = PineconeVectorStoreDriver(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT"),
            index_name=os.getenv("PINECONE_INDEX_NAME"),
        )

        load_data(vector_driver)

        result = vector_driver.query(
            "fruit",
            count=3,
            filter={"price": {"$lte": 15}, "rating": {"$gte": 4}},
            namespace="supermarket-products",
        )

        assert result[0] is not None and result[0].meta is not None
        assert re.search("cherry", result[0].meta['title'], re.IGNORECASE)
